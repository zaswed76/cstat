import sys

from programm.gui import graph, base
from programm import pth
from PyQt5 import QtWidgets

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(open(pth.CSS_STYLE, "r").read())
    prog = base.CStatMain()
    prog.show()
    sys.exit(app.exec_())





if __name__ == '__main__':
    main()
