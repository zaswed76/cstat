import sys

import os

from PyQt5 import QtWidgets

from programm.gui import graph
from programm.libs import config
from programm import pth

from  programm import images_rc

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(open(pth.CSS_STYLE, "r").read())

    clubs = config.get_cfg(os.path.join(pth.CONFIG_DIR, "clubs.yaml"))

    state_cfg = config.get_cfg(
        os.path.join(pth.CONFIG_DIR, "gui_stat.yaml"))

    prog = graph.GraphicsWidget(clubs, state_cfg)
    prog.show()

    sys.exit(app.exec_())





if __name__ == '__main__':
    main()
