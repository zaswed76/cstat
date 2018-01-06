
import sys

import os
from jinja2 import Template


from PyQt5 import QtWidgets, uic
from programm.gui.lib import tools



root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/graph_form.ui")



class Club_Widget(QtWidgets.QFrame):
    def __init__(self, name, tag_name, tag_color=None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_name = tag_name
        self.name = name
        box = tools.Box(tools.Box.horizontal, parent=self, spacing=1)
        self.select_club_btn = tools.Button(name, tag_name,
                                            True, True)
        style = open(os.path.join(pth.CSS_DIR, "club_btn.qss"), "r").read()
        template = Template(style).render(color=tag_color)
        self.select_club_btn.setStyleSheet(template)
        self.select_club_btn.setFixedWidth(100)
        self.set_club_btn = tools.Button(name, "*", False, False)
        self.set_club_btn.setFixedWidth(25)

        box.addWidget(self.select_club_btn)
        box.addWidget(self.set_club_btn)



class ClubsContainer(QtWidgets.QGroupBox):
    def __init__(self, clubs_cfg: dict, title=None):
        super().__init__()
        if title is not None:
            self.setTitle(title)
        self.clubs = {}
        self.group = QtWidgets.QButtonGroup(self)
        self.box = tools.Box(tools.Box.vertical, parent=self, spacing=1)
        self.exclusive_club = QtWidgets.QCheckBox("exclusive")
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
            else: self.group.buttons()[0].setChecked(True)
        else:
            for btn in self.group.buttons():
                if not btn.isChecked():
                    btn.setChecked(False)



    def add_clubs(self, clubs):
        for cl in clubs.values():
            self.clubs[cl["name"]] = Club_Widget(cl["name"],
                                                 cl["tag_name"],
                                                 tag_color=cl["color"],
                                                 )
            self.group.addButton(self.clubs[cl["name"]].select_club_btn)

            self.box.addWidget(self.clubs[cl["name"]])
        self.set_exclusive_club(self.exclusive_club.isChecked())
        self.setLayout(self.box)




class GraphicsWidget(QtWidgets.QWidget):
    def __init__(self, clubs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clubs = clubs
        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Graphics")
        self.clubs_container = ClubsContainer(clubs, title="клубы")
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

