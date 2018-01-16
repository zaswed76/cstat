

import sys

import os
from PyQt5 import QtWidgets, uic
from programm.libs import config
from programm import pth
root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/main_form.ui")

class CStatMain(QtWidgets.QMainWindow):
    def __init__(self, *stack_widgets):
        super().__init__()
        self.stack_widgets = {}

        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Cstat")
        self.tool = self.form.toolBar
        self.stack = QtWidgets.QStackedLayout(self.form.central_Frame)
        self.tool.actionTriggered.connect(self.tool_actions)
        self.actions_names = ["stat", "graph"]
        self._set_actions_tool()

        for w in stack_widgets:

            self.stack_widgets[w.objectName()] = w
            self.stack.addWidget(w)
        print(self.stack_widgets)



    def _set_actions_tool(self):
        for n in self.actions_names:
            act = QtWidgets.QAction(n, self)
            act.setObjectName(n)
            self.tool.addAction(act)

    def tool_actions(self, act):
        self.stack.setCurrentWidget(self.stack_widgets[act.objectName()])


    def closeEvent(self, QCloseEvent):
        for w in self.stack_widgets.values():
            config.save_cfg(os.path.join(pth.CONFIG_DIR, w.name_config), w.state_cfg)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    graph = QtWidgets.QFrame()
    # graph.setFixedSize(100, 100)
    graph.setStyleSheet("background-color: green")
    main = CStatMain(graph)
    main.show()
    sys.exit(app.exec_())