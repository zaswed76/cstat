


import sys
from PyQt5 import QtWidgets, QtGui
from programm import pth
img = pth.PLOT_PATH

class Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)
        box = QtWidgets.QVBoxLayout(self)
        self.lb = QtWidgets.QLabel()
        self.lb.setPixmap(QtGui.QPixmap(img))
        box.addWidget(self.lb)
        self.lb.setStyleSheet("background-color: green")
        btn = QtWidgets.QPushButton(self.lb)
        btn.move(300, 300)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = Widget()
    main.show()
    sys.exit(app.exec_())


