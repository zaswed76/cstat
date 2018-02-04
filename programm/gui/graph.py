import datetime
import os
import sqlite3
import sys
from collections import Counter
from pathlib import PurePath

import pandas as pd
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from jinja2 import Template

from programm import pth
from programm.dataproc import data_proc as dproc
from programm.gui import slider as sl
from programm.gui.lib import tools, service
from programm.gui.plot import plot
from programm.sql import sql_keeper as keeper

root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/graph_form.ui")
from programm.log import log as lg

log = lg.log(os.path.join(pth.LOG_DIR, "graph.log"))


class Club_Widget(QtWidgets.QFrame):
    def __init__(self, name, tag_name, tag_color=None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_name = tag_name
        self.name = name
        box = tools.Box(tools.Box.horizontal, parent=self, spacing=5)
        self.select_club_btn = tools.Button(tag_name, tag_name,
                                            True, True)

        style = Template(
            open(os.path.join(pth.CSS_DIR, "club_btn.qss"),
                 "r").read()).render(color=tag_color)
        self.select_club_btn.setStyleSheet(style)
        self.select_club_btn.setFixedWidth(100)

        self.set_club_btn = tools.Button(tag_name + "_btn_set", None,
                                         False, False)

        self.set_club_btn.setFixedSize(25, 30)

        box.addWidget(self.select_club_btn)
        box.addWidget(self.set_club_btn)


class ClubsContainer(QtWidgets.QGroupBox):
    def __init__(self, clubs_cfg: dict, state_cfg, title=None):
        super().__init__()
        if title is not None:
            self.setTitle(title)
        self._clubs = {}
        self._group = QtWidgets.QButtonGroup(self)
        self.box = tools.Box(tools.Box.vertical, parent=self,
                             spacing=6, margin=(6, 6, 0, 10))
        self.exclusive_club = QtWidgets.QCheckBox("exclusive")
        self.exclusive_club.setChecked(
            state_cfg["clubs_group_exclusive"])
        self.exclusive_club.stateChanged.connect(
            self._exclusive_state)
        self.box.addWidget(self.exclusive_club)
        self._add_clubs(clubs_cfg)

    @property
    def club_buttons(self):
        return self._group.buttons()

    def _exclusive_state(self):
        self._set_exclusive_club(self.exclusive_club.isChecked())

    def _set_exclusive_club(self, state):
        self._group.setExclusive(state)
        check_btn = self._group.checkedButton()
        if state:
            for btn in self._group.buttons():
                btn.setChecked(False)
            if check_btn is not None:
                check_btn.setChecked(True)
            else:
                self._group.buttons()[0].setChecked(True)
        else:
            for btn in self._group.buttons():
                if not btn.isChecked():
                    btn.setChecked(False)

    def _add_clubs(self, clubs):
        for cl in clubs.values():
            self._clubs[cl["name"]] = Club_Widget(cl["name"],
                                                  cl["tag_name"],
                                                  tag_color=cl[
                                                      "color"],
                                                  )
            self._group.addButton(
                self._clubs[cl["name"]].select_club_btn)

            self.box.addWidget(self._clubs[cl["name"]])
        self._set_exclusive_club(self.exclusive_club.isChecked())
        self.setLayout(self.box)


class GraphicsWidget(QtWidgets.QWidget):
    def __init__(self, name, clubs, state_cfg, name_config=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graphic_types = {"period": self.set_period_plot,
                              "one_shift": self.set_one_shift_plot}

        self.current_club_show = None

        self.name_config = name_config
        self.state_cfg = state_cfg

        self.clubs = clubs

        self.form = uic.loadUi(ui_pth, self)
        self.setObjectName(name)
        self.setWindowTitle("Graphics")
        self.resize(1200, 622)
        self.clubs_container = ClubsContainer(clubs, state_cfg,
                                              title="клубы", )
        self.form.clube_layout.addWidget(self.clubs_container)
        self.__db_path = self.get_last_bd_path()
        self.form.shoose_db.setText(
            self._get_label_path_text(self.__db_path))
        self.__init_date_widgets()
        self.__init_diapason_slider()
        self._init_control()

    def choose_db_dialog(self):
        file_name = service.choose_db_dialog(
            self.state_cfg["last_data_dir"])
        if file_name:
            self.form.shoose_db.setText(
                self._get_label_path_text(file_name))
            self.state_cfg["last_data_path"] = file_name
            self.state_cfg["last_data_dir"] = os.path.dirname(
                file_name)

    def _get_label_path_text(self, path):
        pp = PurePath(path).parts
        a = os.path.join(*pp[:2])
        b = pp[-1]
        return "{} ... {}".format(a, b)

    def __init_date_widgets(self):
        yesterday_dt = datetime.datetime.now() - datetime.timedelta(
            days=1)
        current_dt = datetime.datetime.now()
        d_start = yesterday_dt.date()
        # d_start = current_dt.date()
        t_start = datetime.datetime.strptime("9:00", "%H:%M").time()
        self.form.dt_start_edit.setDate(d_start)
        # self.form.dt_start_edit.setDate(datetime.datetime.strptime("2017-12-27", "%Y-%m-%d").date())
        self.form.time_start_edit.setTime(t_start)

        d_end = current_dt.date()
        t_end = datetime.datetime.strptime("7:59", "%H:%M").time()
        self.form.dt_end_edit.setDate(d_end)

        self.form.time_end_edit.setTime(t_end)

        # y_limit=(0, current_club_cfg["graphics_max"])

        self.plot_view = plot.Graphic()

        self.grid = self.form.graph_grid_

        self.tl_lb = GraphicLabel("top_left_glabel")
        self.tr_lb = GraphicLabel("top_right_glabel")
        self.bl_lb = GraphicLabel("bot_left_glabel")
        self.br_lb = GraphicLabel("bot_right_glabel")
        self.grid.addWidget(self.tl_lb, 0, 0)
        self.grid.addWidget(self.tr_lb, 0, 1)
        self.grid.addWidget(self.bl_lb, 1, 0)
        self.grid.addWidget(self.br_lb, 1, 1)

    def __init_diapason_slider(self):
        self.slider = sl.SliderDiapasonWidget(QtCore.Qt.Horizontal,
                                              mark_names=["10 м",
                                                          "30 м",
                                                          " 1 ч",
                                                          " 1 д"])
        self.slider.slider.valueChanged.connect(self.diapason_change)
        self.form.diapason_box.addWidget(self.slider)

    def _init_control(self):
        for btn in self.clubs_container.club_buttons:
            btn.clicked.connect(self._check_club)
        self.form.shoose_db.clicked.connect(self.choose_db_dialog)

    def _check_club(self):
        self.update_plot()

    def diapason_change(self):
        pass

    def get_controller_data(self):
        d = {}
        d["date_start"] = self.get_date_start()
        d["date_end"] = self.get_date_end()
        d["time_start"] = self.get_time_start()
        d["time_end"] = self.get_time_end()
        d["active_clubs"] = self.get_active_clubs()
        d["interval"] = self.get_interval()
        d["db_path"] = self.get_db_path()
        return d

    def get_graphic_type(self, controller_data):
        st = controller_data["date_start"]
        end = controller_data["date_end"]
        delta = end - st
        if delta == datetime.timedelta(days=1):
            gtype = "one_shift"
        elif delta > datetime.timedelta(days=1):
            gtype = "period"
        else:
            gtype = None
        return gtype

    def show_plot(self, view, path=""):
        view.save_from_file(path)
        view.close()
        self.bl_lb.setPixmap(QtGui.QPixmap(pth.PLOT_PATH))

    def clear_plot(self, view):
        view.close()
        self.bl_lb.clear()

    def update_plot(self):
        controller_data = self.get_controller_data()
        graphic_name_type = self.get_graphic_type(controller_data)
        if graphic_name_type is not None:
            graphic_type_method = self.graphic_types[graphic_name_type]
            graphic_type_method(controller_data)
        else:
            log.warning("нельзя построить такой график")

    def get_period_data(self, controller_data):
        data_dict = {}
        bd_path = self.get_last_bd_path()
        club_name = controller_data['active_clubs'][0]
        self.current_club_show = club_name
        self.current_club_cfg = self.clubs[club_name]
        data_stat_arg = dict(table_name="club",
                             club_name=self.current_club_cfg["name"],
                             controller_data=controller_data,
                             db_path=bd_path)
        stat_data = dproc.get_data(**data_stat_arg)
        if stat_data is not None:

            # stat_data["data_time"] = pd.to_datetime(stat_data["data_time"])
            stat_data.loc[:, "data_time"] = stat_data.data_time.astype('datetime64[ns]')

            # список уникльных отсортированых дат - (начало, конец) < pd.Timestamp
            start_end_dates = dproc.get_start_end_dates(
                stat_data,
                self.current_club_cfg["work_time"]["start"],
                self.current_club_cfg["work_time"]["end"])

            every_days_data = dproc.get_data_every_day(stat_data, "data_time",
                                                       start_end_dates,
                                                       mean_columns=["visitor"])

            data_dict["d_days"] = [x.day for x in every_days_data["data_time"]]
            data_dict["d_visitor"] = every_days_data["visitor"].tolist()

            # -------------------------------------------------------------
            data_table_arg = dict(table_name="club_tab",
                                  club_name=self.current_club_cfg[
                                      "name"],
                                  controller_data=controller_data,
                                  db_path=bd_path)
            data_table = dproc.get_data(**data_table_arg)

            pro_comp_list = map(str,
                                self.current_club_cfg[
                                    "pro_comp_list"])
            # пк указанные в списке pro_comp_list
            pro_data = data_table[
                data_table["ncomp"].isin(pro_comp_list)]
            include_active_classes = self.current_club_cfg[
                "include_active_classes"]
            # пк класс которых значится как активные
            # активные классы указны в списке include_active_classes
            active_pro_data = pro_data[
                pro_data["class"].isin(include_active_classes)]

            # active_pro_data["data_time"] = pd.to_datetime(active_pro_data["data_time"])
            active_pro_data.loc[:, "data_time"] = active_pro_data.data_time.astype('datetime64[ns]')
            pro_mean_data = dproc.get_data_table_every_day(active_pro_data, "data_time",
                                                           start_end_dates,
                                                           mean_columns=["visitor"])

            data_dict["d_pro"] = [int(round(x)) for x in pro_mean_data["visitor"]]


            data_dict["d_days_colors"] = dproc.date_colors(every_days_data["data_time"],
                                                           [5, 6], "r", "black")


            return data_dict
        else:
            return None

    def set_period_plot(self, controller_data):
        data = self.get_period_data(controller_data)
        if data:
            self.plot_view.plot(data.get("d_days"),
                                data.get("d_visitor"),
                                color=self.current_club_cfg["color"],
                                width=self.current_club_cfg["width"],
                                name="visitors",
                                title=self.current_club_cfg["tag_name"],
                                grid=True)

            self.plot_view.plot(data.get("d_days"),
                                data.get("d_pro"),
                                color=self.current_club_cfg[
                                    "pro_color"],
                                y_limit=(
                                    0,
                                    self.current_club_cfg[
                                        "graphics_max"]),
                                width=0.2,
                                name="pro",
                                grid=True,
                                dey_colors=data.get("d_days_colors")
                                )

            self.plot_view.add_horizontal_line(
                self.current_club_cfg["max"],
                len(data.get("d_days")),
                color=self.current_club_cfg["max_pc_color"],
                text="pc max")

            self.plot_view.add_horizontal_line(
                len(self.current_club_cfg["pro_comp_list"]),
                len(data.get("d_days")),
                color=self.current_club_cfg["pro_color"],
                text="pro max")

            self.show_plot(self.plot_view)

    def get_one_shift_data(self, controller_data):
        data_dict = {}
        bd_path = self.get_last_bd_path()
        club_name = controller_data['active_clubs'][0]
        self.current_club_show = club_name
        self.current_club_cfg = self.clubs[club_name]
        data_stat_arg = dict(table_name="club",
                             club_name=self.current_club_cfg["name"],
                             controller_data=controller_data,
                             db_path=bd_path)
        stat_data = dproc.get_data(**data_stat_arg)

        count_measurements_hour = dproc.measurements_hour(stat_data)

        if stat_data is None:
            log.warning("файл не является базой данных")
            self.clear_plot(self.plot_view)
            return
        elif stat_data.empty:
            log.warning("нет данных")
            self.clear_plot(self.plot_view)
            return
        else:
            # усреднённые данные числовых колонок
            every_hour_data = dproc.get_data_every_time(stat_data, "mhour")

            data_dict["h_hours"] = every_hour_data["mhour"]
            data_dict["h_visitor"] = [int(round(x)) for x in
                                      every_hour_data["visitor"]]
            data_dict["h_school"] = [int(round(x)) for x in
                                     every_hour_data["school"]]

            pro_comp_list = map(str,
                                self.current_club_cfg[
                                    "pro_comp_list"])
            data_table_arg = dict(table_name="club_tab",
                                  club_name=self.current_club_cfg[
                                      "name"],
                                  controller_data=controller_data,
                                  db_path=bd_path)
            data_table = dproc.get_data(**data_table_arg)

            # пк указанные в списке pro_comp_list
            pro_data = data_table[
                data_table["ncomp"].isin(pro_comp_list)]

            include_active_classes = self.current_club_cfg[
                "include_active_classes"]

            # пк класс которых значится как активные
            # активные классы указны в списке include_active_classes
            active_pro_data = pro_data[
                pro_data["class"].isin(include_active_classes)]
            # pd.DataFrame columns=["mhour","mean"] mean:float(0, ..)
            # средние показатели в посетителях покаждому часу

            pro_mean_data = dproc.mean_hourly_data(data_dict["h_hours"],
                                                   count_measurements_hour,
                                                   active_pro_data)


            working_club_hours = self.current_club_cfg["working_hours"]
            real_hours = pro_mean_data["mean"].size
            if real_hours < working_club_hours:
                size_hours = real_hours
            else:
                size_hours = working_club_hours

            pro_mean = pro_mean_data["mean"].sum() / size_hours


            print("{data}\nпосетителей на про зоне среднее  за день {mean}".format(mean=pro_mean,
                                                                       data=controller_data["date_start"]))
            print("------------------------")
            data_dict["percentage_ratio_pro"] = round(dproc.percentile(
                len(self.current_club_cfg["pro_comp_list"]),
                pro_mean), 1)

            data_dict["occupied_pro_max"] = dproc.time_occupied(pro_mean_data,
                                                                "mean",
                                                                len(
                                                                    self.current_club_cfg[
                                                                        "pro_comp_list"]),
                                                                data_dict[
                                                                    "h_hours"].size)

            data_dict["occupied_pro_min"] = dproc.time_occupied(pro_mean_data,
                                                                "mean", 0,
                                                                data_dict[
                                                                    "h_hours"].size)

            data_dict["h_pro"] = [int(round(x)) for x in pro_mean_data["mean"]]

            data_dict["mean_visitor"] = dproc.get_mean_people(stat_data["visitor"])

            data_dict["mean_load"] = dproc.get_mean_load(data_dict["mean_visitor"],
                                                         self.current_club_cfg[
                                                             "max"])

            data_school_time = dproc.data_period_time(
                controller_data["date_start"],
                self.current_club_cfg["school_time"], stat_data,
                "data_time")

            data_dict["percentage_ratio_school"] = dproc.get_percentage_ratio(
                data_school_time, "visitor", "school")
        return data_dict

    def set_one_shift_plot(self, controller_data):
        data = self.get_one_shift_data(controller_data)
        if data:
            self.plot_view.plot(data.get("h_hours"),
                                data.get("h_visitor"),
                                color=self.current_club_cfg["color"],
                                width=self.current_club_cfg["width"],
                                name="visitors",
                                title=self.current_club_cfg["tag_name"])

            self.plot_view.plot(data.get("h_hours"),
                                data.get("h_school"),
                                color=self.current_club_cfg[
                                    "school_color"],
                                y_limit=(
                                    0,
                                    self.current_club_cfg[
                                        "graphics_max"]),
                                width=self.current_club_cfg[
                                          "width"] - 0.1,
                                name="school")
            self.plot_view.plot(data.get("h_hours"),
                                data.get("h_pro"),
                                color=self.current_club_cfg[
                                    "pro_color"],
                                y_limit=(
                                    0,
                                    self.current_club_cfg[
                                        "graphics_max"]),
                                width=0.2,
                                name="pro",
                                grid=True
                                )
            self.plot_view.set_legend(["visitors", "school", "pro"])
            self.plot_view.add_horizontal_line(
                self.current_club_cfg["max"],
                len(data.get("h_pro")),
                color=self.current_club_cfg["max_pc_color"],
                text="pc max")
            self.plot_view.add_horizontal_line(
                len(self.current_club_cfg["pro_comp_list"]),
                len(data.get("h_hours")),
                color=self.current_club_cfg["pro_color"],
                text="pro max")

            text1 = """человек в среднем - {}
заполненность клуба - {}%
процент школьников - {}%""".format(data.get("mean_visitor"),
                                   data.get("mean_load"),
                                   data.get(
                                       "percentage_ratio_school"))

            text2 = """про зона используется на - {}%
про зона занята на 100% - {}% времени
про зона вообще не занята - {}% времени""".format(
                data.get("percentage_ratio_pro"),
                data.get("occupied_pro_max"),
                data.get("occupied_pro_min"))

            self.plot_view.text(text1, 'left-top-over')
            self.plot_view.text(text2, 'center-top-over')
            self.show_plot(self.plot_view)

    def get_date_start(self) -> datetime.datetime:
        return self.form.dt_start_edit.dateTime().toPyDateTime().date()

    def get_date_end(self) -> datetime.datetime:
        return self.form.dt_end_edit.dateTime().toPyDateTime().date()

    def get_time_start(self) -> datetime.datetime:
        return self.form.time_start_edit.dateTime().toPyDateTime().time()

    def get_time_end(self) -> datetime.datetime:
        return self.form.time_end_edit.dateTime().toPyDateTime().time()

    def get_active_clubs(self) -> list:
        return [x.tag_name for x in self.clubs_container.club_buttons
                if x.isChecked()]

    def get_interval(self) -> str:
        return "1 h"

    def get_db_path(self) -> str:
        return self.__db_path

    def get_last_bd_path(self):
        return self.state_cfg["last_data_path"]

    def closeEvent(self, QCloseEvent):

        print("close graph")


class GraphicLabel(QtWidgets.QLabel):
    def __init__(self, name, *__args):
        super().__init__(*__args)
        self.setObjectName(name)

    def create_info_label(self):
        self.btn = InfoBox(self)
        self.btn.setStyleSheet("background-color: lightgrey")
        self.btn.setFixedSize(300, 68)
        self.btn.move(106, -1)
        self.btn.show()
        return self.btn


class InfoBox(QtWidgets.QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid = QtWidgets.QVBoxLayout(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

    def add_text(self, text):
        lb = InfoLabel(text)
        lb.setScaledContents(True)
        self.grid.addWidget(lb)


class InfoLabel(QtWidgets.QLabel):
    def __init__(self, *__args):
        super().__init__(*__args)


if __name__ == '__main__':
    from programm.libs import config
    from programm import pth

    app = QtWidgets.QApplication(sys.argv)

    clubs = config.get_cfg(os.path.join(pth.CONFIG_DIR, "clubs.yaml"))

    state_cfg = config.get_cfg(
        os.path.join(pth.CONFIG_DIR, "gui_stat.yaml"))

    main = GraphicsWidget(clubs, state_cfg)
    app.setStyleSheet(open(pth.CSS_STYLE, "r").read())
    main.show()
    sys.exit(app.exec_())
