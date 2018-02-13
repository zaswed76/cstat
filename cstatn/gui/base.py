

import sys
import shutil
import os
from PyQt5 import QtWidgets, uic
from cstatn.libs import config
from cstatn import pth
from cstatn.gui.lib import service
root = os.path.join(os.path.dirname(__file__))
ui_pth = os.path.join(root, "ui/main_form.ui")

class CStatMain(QtWidgets.QMainWindow):
    def __init__(self, *stack_widgets, config=None, name_config=None):
        super().__init__()
        self.name_config = name_config
        if config is not None:
            self.cfg = config
        else: self.cfg = {}


        self.stack_widgets = {}

        self.form = uic.loadUi(ui_pth, self)
        self.setWindowTitle("Cstat")
        self.tool = self.form.toolBar
        self.stack = QtWidgets.QStackedLayout(self.form.central_Frame)
        self.tool.actionTriggered.connect(self.tool_actions)
        self.actions_names = ["stat", "graph", "save"]
        self._set_actions_tool()

        for w in stack_widgets:
            self.stack_widgets[w.objectName()] = w
            self.stack.addWidget(w)
        self.resize(*self.cfg.get("size", (800, 600)))



    def _set_actions_tool(self):
        for n in self.actions_names:
            act = QtWidgets.QAction(n, self)
            act.setObjectName(n)
            self.tool.addAction(act)

    def tool_actions(self, act):
        meth_name = act.objectName()
        getattr(self, meth_name)(meth_name=meth_name)



    def save(self, **kwargs):
        current_stack = self.stack.currentWidget()
        path = os.path.join(pth.DESKTOP, current_stack.current_club_show + ".png")
        shutil.copy2(pth.PLOT_PATH, path)

    def graph(self, meth_name=None):
        self.stack.setCurrentWidget(self.stack_widgets[meth_name])


    def stat(self, meth_name=None):
        self.stack.setCurrentWidget(self.stack_widgets[meth_name])

    def closeEvent(self, QCloseEvent):
        wind_size = [self.size().width(), self.size().height()]
        self.cfg["size"] = wind_size
        config.save_cfg(os.path.join(pth.CONFIG_DIR, self.name_config), self.cfg)
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