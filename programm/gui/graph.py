import datetime
import os
import sys

from PyQt5 import QtWidgets, uic, QtCore

from jinja2 import Template
from programm import pth
from programm.gui.lib import tools
from programm.gui.plot import plot
from programm.gui import slider as sl

root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/graph_form.ui")


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
    def __init__(self, clubs, state_cfg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_cfg = state_cfg
        self.clubs = clubs
        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Graphics")
        self.clubs_container = ClubsContainer(clubs, state_cfg,
                                              title="клубы", )
        self.form.clube_layout.addWidget(self.clubs_container)
        self.form.shoose_db.setText(self.get_last_bd_path())
        self.__init_date_widgets()
        self.__init_diapason_slider()
        self._init_control()

    def choose_db_dialog(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py)",
                                                            options=options)
        if fileName:
            text = os.path.basename(fileName)
            self.form.shoose_db.setText(text)



    def __init_date_widgets(self):
        yesterday_dt = datetime.datetime.now() - datetime.timedelta(
            days=1)
        d_start = yesterday_dt.date()
        t_start = datetime.datetime.strptime("09:00", "%H:%M").time()
        self.form.dt_start_edit.setDate(d_start)
        self.form.time_start_edit.setTime(t_start)

        current_dt = datetime.datetime.now()
        d_end = current_dt.date()
        t_end = datetime.datetime.strptime("09:00", "%H:%M").time()
        self.form.dt_end_edit.setDate(d_end)
        self.form.time_end_edit.setTime(t_end)


        self.update_plot()

        # self.view = self.form.graph_frame
        # m = plot.PlotCanvas(None, width=5, height=4)
        # self.form.view_box.addWidget(m)

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
            btn.toggled.connect(self._check_club)
        self.form.shoose_db.clicked.connect(self.choose_db_dialog)

    def _check_club(self):
        print([x for x in self.clubs_container.club_buttons if
               x.isChecked()])

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
        # данные с контроллеров
        controller_data = self.get_controller_data()
        # запрос
        sql_query = self.get_sql_query(controller_data)
        # данные
        data = self.get_data(sql_query)

    def get_date_start(self) -> datetime.datetime:
        return self.form.dt_start_edit.dateTime().toPyDateTime().date()

    def get_date_end(self) -> datetime.datetime:
        return self.form.dt_end_edit.dateTime().toPyDateTime().date()

    def get_time_start(self) -> datetime.datetime:
        return self.form.time_start_edit.dateTime().toPyDateTime().time()

    def get_time_end(self) -> datetime.datetime:
        return self.form.time_end_edit.dateTime().toPyDateTime().time()

    def get_active_clubs(self) -> list:
        return ["Les"]

    def get_graphic_type(self) -> str:
        return "bar"

    def get_interval(self) -> str:
        return "1 h"

    def get_db_path(self) -> str:
        return ""

    def get_sql_query(self, data) -> str:
        return "sql_query"

    def get_data(self, query) -> tuple:
        return ()

    def get_last_bd_path(self):
        return "11-01-2018-db.sql"


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
