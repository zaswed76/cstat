

import sys
from PyQt5 import QtWidgets, QtGui
from programm import pth

class Widget(QtWidgets.QLabel):
    def __init__(self):
        super().__init__()
        self.box = QtWidgets.QHBoxLayout(self)
        self.fr = QtWidgets.QFrame()
        self.fr.setFixedWidth(100)
        self.fr.setStyleSheet("background-color: green")
        self.box.addWidget(self.fr)

        self.setScaledContents(True)

        self.pxm = QtGui.QPixmap(pth.PLOT_PATH)

        self.setPixmap(self.pxm)


    # def resizeEvent(self,  event):
    #      if self.pxm is not None:
    #          pixmap = self.pxm
    #          size = event.size()
    #          print(size)
    #          self.lb.setPixmap(pixmap)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = Widget()
    main.show()
    sys.exit(app.exec_())