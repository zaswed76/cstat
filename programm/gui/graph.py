
import sys

import os
from PyQt5 import QtWidgets, uic


root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/graph_form.ui")

class GraphicsWidget(QtWidgets.QWidget):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Graphics")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = GraphicsWidget()
    main.show()
    sys.exit(app.exec_())

