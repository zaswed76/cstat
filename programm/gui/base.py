

import sys

import os
from PyQt5 import QtWidgets, uic

root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/main_form.ui")

class CStatMain(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Cstat")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = CStatMain()
    main.show()
    sys.exit(app.exec_())