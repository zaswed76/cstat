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
        self.__init_date_widgets()
        self.__init_diapason_slider()
        self._init_control()

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
        # slider.setRange(0, 3)
        # slider.setSingleStep(1)
        # slider.setPageStep(1)
        # slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

    def _init_control(self):
        for btn in self.clubs_container.club_buttons:
            btn.toggled.connect(self._check_club)

    def _check_club(self):
        print([x for x in self.clubs_container.club_buttons if
               x.isChecked()])

    def diapason_change(self):
        print("3")

    def update_plot(self):
        print("update plot")
        # получить данные контроллеров
        # сделать запрос к базе
        # обновить график


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
