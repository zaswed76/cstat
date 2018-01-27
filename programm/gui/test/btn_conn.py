
import sys
from PyQt5 import QtWidgets

class Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 500)
        self.btn = QtWidgets.QPushButton(self)
        self.btn.setCheckable(True)
        self.btn.setObjectName('tag_name')
        self.btn.setAutoExclusive(True)
        self.btn.clicked.connect(self.click_btn)

    def click_btn(self):
        print("btn")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = Widget()
    main.show()
    sys.exit(app.exec_())