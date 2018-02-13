import sys

import os

from PyQt5 import QtWidgets, QtCore

from cstatn import pth
# from cstatn.gui import graph, base
# from cstatn.libs import config
# from cstatn import pth
#
# from  cstatn import images_rc

def qt_message_handler(mode, context, message):
    if mode == QtCore.QtInfoMsg:
        mode = 'INFO'
    elif mode == QtCore.QtWarningMsg:
        mode = 'WARNING'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'CRITICAL'
    elif mode == QtCore.QtFatalMsg:
        mode = 'FATAL'
    else:
        mode = 'DEBUG'
    print('qt_message_handler: line: %d, func: %s(), file: %s' % (
        context.line, context.function, context.file))
    print('  %s: %s\n' % (mode, message))


QtCore.qInstallMessageHandler(qt_message_handler)



def main():
    print("!!!!!!")
    # app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open(pth.CSS_STYLE, "r").read())
    #
    # clubs = config.get_cfg(os.path.join(pth.CONFIG_DIR, "clubs.yaml"))["clubs"]
    #
    # state_cfg = config.get_cfg(
    #     os.path.join(pth.CONFIG_DIR, "gui_graph.yaml"))
    #
    # gr = graph.GraphicsWidget("graph", clubs, state_cfg, name_config="gui_graph.yaml")
    #
    # stat = QtWidgets.QFrame()
    # stat.name_config = "gui_stat.yaml"
    # stat.state_cfg = {}
    # stat.setObjectName("stat")
    # stat.setStyleSheet("background-color: green")
    # base_config = config.get_cfg(
    #     os.path.join(pth.CONFIG_DIR, "base.yaml"))
    # prog = base.CStatMain(gr, stat, config=base_config, name_config="base.yaml")
    # prog.show()
    #
    # sys.exit(app.exec_())





if __name__ == '__main__':
    main()
