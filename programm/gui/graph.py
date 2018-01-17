import datetime
import os
import sys

import pandas
from PyQt5 import QtWidgets, uic, QtCore, QtGui

from jinja2 import Template
from programm import pth
from programm.gui.lib import tools
from programm.gui.plot import graph, plot
from pathlib import Path, PurePath
from programm.gui import slider as sl
from programm.sql import sql_keeper

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
        print(name, "name")

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

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                            "QFileDialog.getOpenFileName()",
                                                            "",
                                                            "All Files (*);;Python Files (*.py)",
                                                            options=options)
        if fileName:
            self.form.shoose_db.setText(
                self._get_label_path_text(fileName))
            self.state_cfg["last_data_path"] = fileName

    def _get_label_path_text(self, path):
        pp = PurePath(path).parts
        a = os.path.join(*pp[:2])
        b = pp[-1]
        return "{} ... {}".format(a, b)

    def __init_date_widgets(self):
        yesterday_dt = datetime.datetime.now() - datetime.timedelta(
            days=1)
        d_start = yesterday_dt.date()
        t_start = datetime.datetime.strptime("9:00", "%H:%M").time()
        self.form.dt_start_edit.setDate(d_start)
        # self.form.dt_start_edit.setDate(datetime.datetime.strptime("2017-12-27", "%Y-%m-%d").date())
        self.form.time_start_edit.setTime(t_start)

        current_dt = datetime.datetime.now()
        d_end = current_dt.date()
        t_end = datetime.datetime.strptime("9:01", "%H:%M").time()
        self.form.dt_end_edit.setDate(d_end)
        # self.form.dt_end_edit.setDate(datetime.datetime.strptime("2017-12-27", "%Y-%m-%d").date())
        self.form.time_end_edit.setTime(t_end)

        self.plot_view = plot.Graphic()
        self.graphic_frame = self.form.graphic_frame
        self.grid = self.form.graph_grid

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

    def update_plot(self):
        controller_data = self.get_controller_data()
        path = self.get_last_bd_path()
        data_step = self.get_data(controller_data, path)
        if data_step:
            club = controller_data['active_clubs'][0]
            color = self.clubs[club]["color"]
            time, load, schools, all_data = data_step
            av = self._get_average_people(load)



            if load:
                self.plot_view.plot(time, load, color=color,
                                    y_limit=(0, 50), width=0.8,
                                    name="visitors", title=club)
                self.plot_view.plot(time, schools, color="#FCF355",
                                    y_limit=(0, 50), width=0.7,
                                    name="school")
                self.plot_view.set_bg("#DDDDDD")
                self.plot_view.set_legend([club, "school"])
                self.plot_view.set_grid()
                self.plot_view.save_from_file()

                self.plot_view.close()
                self.bl_lb.setPixmap(QtGui.QPixmap(pth.PLOT_PATH))
                self.info_lb = self.bl_lb.create_info_label()
                average_people = self._get_average_people(
                all_data["visitor"])
                self.info_lb.add_text(
                    "человек в среднем - {}".format(average_people))
                average_load = self._get_average_load(
                    average_people,
                    self.clubs[club]["max"])
                self.info_lb.add_text(
                    "заполненность клуба - {}%".format(average_load))
                # self.info_lb.add_text("школьникв в среднем - 5")
                # self.info_lb.add_text("заполненность клуба - 16%")






        else:
            log.debug("not data")

    def _get_average_people(self, visitor, r=0):
        lenght = len(visitor)
        s = sum(visitor)
        return round(s / lenght)

    def _get_average_load(self, avis, max, r=0):
        r = (avis/max)*100
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

    def get_data(self, controller_data, db_path):
        kp = sql_keeper.Keeper(db_path)

        start = datetime.datetime.combine(
            controller_data["date_start"],
            controller_data["time_start"])
        end = datetime.datetime.combine(controller_data["date_end"],
                                        controller_data["time_end"])
        club = controller_data["active_clubs"]

        n = club[0]

        params = (self.clubs[n]["name"], start, end)

        try:
            d = kp.sample_range_date_time(*params)
            step_data = d["step_data"]
            all_data = d["all_data"]
        except pandas.io.sql.DatabaseError:
            return None
        else:
            mhour = step_data["mhour"].tolist()
            visitor = step_data["visitor"].tolist()
            schools = step_data["school"].tolist()
            return (mhour, visitor, schools, all_data)

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
        self.btn.move(106, -10)
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
