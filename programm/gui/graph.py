
import sys

import os
from PyQt5 import QtWidgets, uic
from programm.gui.lib import tools



root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/graph_form.ui")



class Club_Widget(QtWidgets.QFrame):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        box = tools.Box(tools.Box.horizontal, parent=self)
        self.select_club_btn = tools.Button(name, name, True, True)
        style = os.path.join(pth.CSS_DIR, "club_btn.css")
        self.select_club_btn.setStyleSheet(open(style, "r").read())
        self.select_club_btn.setFixedWidth(100)
        self.set_club_btn = tools.Button(name, "*", False, False)
        self.set_club_btn.setFixedWidth(25)

        box.addWidget(self.select_club_btn)
        box.addStretch(20)
        box.addWidget(self.set_club_btn)



class ClubsContainer(QtWidgets.QGroupBox):
    def __init__(self, clubs_cfg: dict, title=None):
        super().__init__()
        if title is not None:
            self.setTitle(title)
        self.clubs = {}
        self.box = tools.Box(tools.Box.vertical, parent=self)
        self.add_clubs(clubs_cfg)

    def add_clubs(self, clubs):
        for cl in clubs.values():
            self.clubs[cl["name"]] = Club_Widget(cl["name"])
            self.box.addWidget(self.clubs[cl["name"]])
        self.setLayout(self.box)




class GraphicsWidget(QtWidgets.QWidget):
    def __init__(self, clubs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clubs = clubs
        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Graphics")
        self.clubs_container = ClubsContainer(clubs)
        self.form.clube_layout.addWidget(self.clubs_container)



if __name__ == '__main__':
    from programm.libs import config
    from programm import pth
    app = QtWidgets.QApplication(sys.argv)
    cfg_path = os.path.join(pth.CONFIG_DIR, "clubs.yaml")
    clubs = config.get_cfg(cfg_path)

    main = GraphicsWidget(clubs)
    app.setStyleSheet(open(pth.CSS_STYLE, "r").read())
    main.show()
    sys.exit(app.exec_())

