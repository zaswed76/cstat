
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
        self.set_club_btn = tools.Button(name, None, False, False)
        box.add_widgets(self.select_club_btn, self.set_club_btn)



class ClubsContainer(QtWidgets.QFrame):
    def __init__(self, clubs_cfg: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clubs = {}
        self.box = tools.Box(tools.Box.vertical, parent=self)
        self.add_clubs(clubs_cfg)

    def add_clubs(self, clubs):
        for cl in clubs.values():
            self.clubs[cl["name"]] = Club_Widget(cl["name"])
            self.box.addWidget(self.clubs[cl["name"]])




class GraphicsWidget(QtWidgets.QWidget):
    def __init__(self, clubs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clubs = clubs
        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Graphics")



if __name__ == '__main__':
    from programm.libs import config
    from programm import pth
    app = QtWidgets.QApplication(sys.argv)
    cfg_path = os.path.join(pth.CONFIG_DIR, "clubs.yaml")
    clubs = config.get_cfg(cfg_path)

    main = GraphicsWidget(clubs)
    main.show()
    sys.exit(app.exec_())

