import os
import sys

from PyQt5 import QtWidgets, uic
from jinja2 import Template
from programm import pth
from programm.gui.lib import tools
from programm.gui.plot import plot

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


        self.set_club_btn = tools.Button(tag_name+"_btn_set", None, False, False)
        print(self.set_club_btn.objectName())
        self.set_club_btn.setFixedSize(25, 30)

        box.addWidget(self.select_club_btn)
        box.addWidget(self.set_club_btn)


class ClubsContainer(QtWidgets.QGroupBox):
    def __init__(self, clubs_cfg: dict, state_cfg, title=None):
        super().__init__()
        if title is not None:
            self.setTitle(title)
        self.clubs = {}
        self.group = QtWidgets.QButtonGroup(self)
        self.box = tools.Box(tools.Box.vertical, parent=self,
                             spacing=6, margin=(6, 0, 0, 0))
        self.exclusive_club = QtWidgets.QCheckBox("exclusive")
        self.exclusive_club.setChecked(
            state_cfg["clubs_group_exclusive"])
        self.exclusive_club.stateChanged.connect(self.exclusive_state)
        self.box.addWidget(self.exclusive_club)
        self.add_clubs(clubs_cfg)

    def exclusive_state(self):
        self.set_exclusive_club(self.exclusive_club.isChecked())

    def set_exclusive_club(self, state):
        self.group.setExclusive(state)
        check_btn = self.group.checkedButton()
        if state:
            for btn in self.group.buttons():
                btn.setChecked(False)
            if check_btn is not None:
                check_btn.setChecked(True)
            else:
                self.group.buttons()[0].setChecked(True)
        else:
            for btn in self.group.buttons():
                if not btn.isChecked():
                    btn.setChecked(False)

    def add_clubs(self, clubs):
        for cl in clubs.values():
            self.clubs[cl["name"]] = Club_Widget(cl["name"],
                                                 cl["tag_name"],
                                                 tag_color=cl[
                                                     "color"],
                                                 )
            self.group.addButton(
                self.clubs[cl["name"]].select_club_btn)

            self.box.addWidget(self.clubs[cl["name"]])
        self.set_exclusive_club(self.exclusive_club.isChecked())
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

        self.view = self.form.graph_frame
        m = plot.PlotCanvas(None, width=5, height=4)
        self.form.view_box.addWidget(m)

    def check_club(self, c):
        print(c, "check")


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
