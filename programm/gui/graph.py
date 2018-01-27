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
        # d_start = yesterday_dt.date()
        d_start = current_dt.date()
        t_start = datetime.datetime.strptime("9:00", "%H:%M").time()
        self.form.dt_start_edit.setDate(d_start)
        # self.form.dt_start_edit.setDate(datetime.datetime.strptime("2017-12-27", "%Y-%m-%d").date())
        self.form.time_start_edit.setTime(t_start)

        d_end = current_dt.date()
        t_end = datetime.datetime.strptime("9:01", "%H:%M").time()
        self.form.dt_end_edit.setDate(d_end)
        # self.form.dt_end_edit.setDate(datetime.datetime.strptime("2017-12-27", "%Y-%m-%d").date())
        self.form.time_end_edit.setTime(t_end)

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
            print("555")
            btn.clicked.connect(self._check_club)
        self.form.shoose_db.clicked.connect(self.choose_db_dialog)

    def _check_club(self):
        self.update_plot()

    def diapason_change(self):
        print("3")

    def get_controller_data(self):
        d = {}
        d["date_start"] = self.get_date_start()
        d["date_end"] = self.get_date_end()
        d["time_start"] = self.get_time_start()
        d["time_end"] = self.get_time_end()
        d["active_clubs"] = self.get_active_clubs()
        d["interval"] = self.get_interval()
        d["graphic_type"] = self.get_graphic_type()
        d["db_path"] = self.get_db_path()
        return d

    def _get_data_every_time(self,
                             data: pd.DataFrame) -> pd.DataFrame:
        m_col = ['taken', 'free',
                 'guest', 'resident', 'admin', 'workers', 'school',
                 'visitor']
        list_res = []
        hour_lst = data["mhour"].unique()
        club = data["club"][0]
        date = data["dt"][0]
        for h in hour_lst:
            lst = [date, pd.NaT, h, 0, club, pd.NaT]
            ser = data[data["mhour"].between(h, h)]
            lst.extend(ser[m_col].mean())
            list_res.append(lst)
        res = pd.DataFrame(list_res, columns=data.columns)
        return res

    def _get_visitor_every_time(self, data, name_column):
        vis = {}
        for t, d in data.items():
            vis[t] = d[name_column]
        return vis

    def show_plot(self, view, path=""):
        view.save_from_file(path)
        view.close()
        self.bl_lb.setPixmap(QtGui.QPixmap(pth.PLOT_PATH))

    def update_plot(self):
        controller_data = self.get_controller_data()

        bd_path = self.get_last_bd_path()
        club_name = controller_data['active_clubs'][0]
        self.current_club_show = club_name
        current_club_cfg = self.clubs[club_name]
        data_stat_arg = dict(table_name="club",
                        club_name=current_club_cfg["name"],
                        controller_data=controller_data,
                        db_path=bd_path)
        stat_data = dproc.get_data(**data_stat_arg)
        if stat_data is None:
            log.warning("файл не является базой данных")
            return
        elif stat_data.empty:
            log.warning("нет данных")
            return
        else:

            pro_comp_list = map(str,
                                current_club_cfg["pro_comp_list"])
            data_table_arg = dict(table_name="club_tab",
                            club_name=current_club_cfg["name"],
                            controller_data=controller_data,
                            db_path=bd_path)
            data_table = dproc.get_data(**data_table_arg)

            pro_data = data_table[
                data_table["ncomp"].isin(pro_comp_list)]

            include_active_classes = current_club_cfg[
                "include_active_classes"]

            active_pro_data = pro_data[
                pro_data["class"].isin(include_active_classes)]
            pro_average = dproc.average_hourly_values(active_pro_data, ["visitor", "school"])



            # print(active_pro_data)

            # every_hour_data = self._get_data_every_time(stat_data)
            # print(every_hour_data)
            # h_hours = every_hour_data["mhour"]
            # h_visitor = [int(round(x)) for x in every_hour_data["visitor"]]
            # h_school = [int(round(x)) for x in every_hour_data["school"]]

            # self.plot_view.plot(h_hours,
            #                     h_visitor,
            #                     color=current_club_cfg["color"],
            #                     y_limit=(0, current_club_cfg["graphics_max"]),
            #                     width=current_club_cfg["width"],
            #                     name="visitors", title=club_name)
            #
            # self.plot_view.plot(h_hours,
            #                     h_school,
            #                     color=current_club_cfg["school_color"],
            #                     y_limit=(0, current_club_cfg["graphics_max"]),
            #                     width=current_club_cfg["width"]-0.1,
            #                     name="school")
            #
            #
            #
            # self.show_plot(self.plot_view)


            # visitor_every = self._get_visitor_every_time(every_hour_data, "visitor")
            # school_every = self._get_visitor_every_time(every_hour_data, "school")
            # print(visitor_every)
            # print("-----------------")
            # print(school_every)


            # mhour = step_data["mhour"].tolist()
            # visitor = step_data["visitor"].tolist()
            # schools = step_data["school"].tolist()
            # data_table = self.get_data_table_club(controller_data, bd_path)
            # pro_zone = current_club_cfg["pro_comp_list"]
            # pzl = [str(x) for x in pro_zone]
            # pro_data = data_table[data_table["ncomp"].isin(pzl)]

            # include_active_classes = current_club_cfg[
            #     "include_active_classes"]
            #
            # active_pro_zone = pro_data[
            #     pro_data["class"].isin(include_active_classes)]
            # #
            # pro_time, pro_vis = self.get_pro_data_step(active_pro_zone)
            #
            # # print(active_pro_zone)
            # # записей
            # count_notes = len(active_pro_zone["data_time"].unique())
            # active = active_pro_zone.count()[0]
            # all_pro = len(pro_zone)
            # print(active , all_pro , count_notes)
            # if active:
            #     # print(active, all_pro, count_notes)
            #     pro_proc = round((active / (all_pro * count_notes)) * 100,

            #                      1)
            # else:
            #     pro_proc = 0

            # if data_step:
            #     print(data_step == True)
            #     color = current_club_cfg["color"]
            #     time, load, schools, all_data = data_step
            #
            #     school_time = current_club_cfg["school_time"]
            #     # школьное время
            #     st, end = self._get_date_school(
            #         controller_data["date_start"], school_time)
            #
            #     data_school = self.get_data_school_time(st, end, all_data)
            #     av_sc = self._get_average_school(data_school["visitor"],
            #                                      data_school["school"])
            #
            #     if load:
            #         self.plot_view.plot(time, load, color=color,
            #                             y_limit=(0, 50), width=0.8,
            #                             name="visitors", title=club_name)


        #
        #                 rsvis = [0] * len(time)
        #
        #                 for n, t in enumerate(time):
        #                     if t in pro_time:
        #                         i = pro_time.index(t)
        #                         rsvis[n] = pro_vis[i]
        #
        #                 self.plot_view.plot(time, rsvis,
        #                                     color=current_club_cfg["pro_color"],
        #                                     y_limit=(0, 50), width=0.2,
        #                                     name="pro")
        #
        #                 self.plot_view.set_bg("#DDDDDD")
        #                 self.plot_view.set_legend([club_name, "school"])
        #                 self.plot_view.add_horizontal_line(
        #                     current_club_cfg["max"],
        #                     len(time),
        #                     color=current_club_cfg["max_pc_color"],
        #                     text="pc max")
        #
        #                 self.plot_view.add_horizontal_line(
        #                     len(current_club_cfg["pro_comp_list"]),
        #                     len(time),
        #                     color=current_club_cfg["pro_color"],
        #                     text="pro max")
        #                 # self.plot_view.set_grid()
        #
        #                 average_people = self._get_average_people(
        #                     all_data["visitor"])
        #
        #                 average_load = self._get_average_load(
        #                     average_people,
        #                     current_club_cfg["max"])
        #                 text = """человек в среднем - {}
        # заполненность клуба - {}%
        # процент школьников - {}%
        # процент использования про зоны - {}%""".format(average_people,
        #                                                average_load,
        #                                                av_sc, pro_proc)
        #                 self.plot_view.set_text(text)

        #
        #         else:
        #
        #             self.current_club_show = None
        #             log.debug("not data")

    def _counter_to_list(self, counter):
        times = list(counter.keys())
        visitors = list(counter.values())
        return times, visitors

    def get_pro_data_step(self, pro_data):
        act_h = pro_data[pro_data["mminute"] == 0]
        cnt = Counter(act_h["mhour"].tolist())
        times, visitors = self._counter_to_list(cnt)

        return times, visitors

    def _get_average_people(self, visitor, r=0):
        lenght = len(visitor)
        s = sum(visitor)
        return round(s / lenght)

    def _get_average_school(self, visitor, school, r=0):
        vs = sum(visitor)
        ss = sum(school)
        if vs:
            r = (ss * 100) / vs
        else:
            r = 0
        return round(r, 1)

    def _get_average_load(self, avis, max, r=0):
        r = (avis / max) * 100
        return round(r, 1)

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

    def get_graphic_type(self) -> str:
        return "bar"

    def get_interval(self) -> str:
        return "1 h"

    def get_db_path(self) -> str:
        return self.__db_path

    def get_sql_query(self, data) -> str:
        return "SELECT * FROM club WHERE (club = ?) AND (data_time BETWEEN ? AND ?)"

    def get_data_school_time(self, st, end, d):
        # print(d, 99999)
        return d[(d["data_time"] > st) & (d["data_time"] < end)]

    def _get_date_school(self, date, time):
        st = time[0].split(":")
        end = time[1].split(":")
        school_time_st = datetime.datetime.strptime(
            '{}:{}'.format(*st), '%H:%M').time()
        school_time_end = datetime.datetime.strptime(
            '{}:{}'.format(*end), '%H:%M').time()

        date_st = datetime.datetime.combine(date,
                                            school_time_st).strftime(
            "%Y-%m-%d %H:%M:%S")
        date_end = datetime.datetime.combine(date,
                                             school_time_end).strftime(
            "%Y-%m-%d %H:%M:%S")
        return date_st, date_end

    def get_data_table_club(self, controller_data, db_path):
        kp = keeper.Keeper(db_path)

        start = datetime.datetime.combine(
            controller_data["date_start"],
            controller_data["time_start"])
        end = datetime.datetime.combine(controller_data["date_end"],
                                        controller_data["time_end"])
        club = controller_data["active_clubs"]

        n = club[0]

        params = (self.clubs[n]["name"], start, end)

        try:
            d = kp.sample_range_date_time_table(*params)
            all_data = d["all_data"]
        except pd.io.sql.DatabaseError:
            return None
        except sqlite3.OperationalError:
            return None
        else:
            return all_data

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
