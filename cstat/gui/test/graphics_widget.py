
import sys

import os
from PyQt5 import QtWidgets


from cstat.gui import graph
from cstat.libs import config
from cstat import pth
cfg_path = os.path.join(pth.CONFIG_DIR, "clubs.yaml")
clubs = config.get_cfg(cfg_path)

def club_widget():
    app = QtWidgets.QApplication(sys.argv)
    main = graph.Club_Widget("les")
    main.show()
    sys.exit(app.exec_())

def clubs_container():
    app = QtWidgets.QApplication(sys.argv)
    main = graph.ClubsContainer(clubs, "клубы")
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    pass
    clubs_container()
    # club_widget()




