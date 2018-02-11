

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QObject

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



class Axes(QtWidgets.QGraphicsItem):
    def __init__(self, scene, pen=None):
        super().__init__()

        self.pen = pen
        self.scene = scene
        self.scene_rect = self.scene.sceneRect()
        self.width = self.scene_rect.width()
        self.height = self.scene_rect.height()
        self.color = QtGui.QColor("green")

    def set_pen(self, pen):
        self.pen = pen

    def paint(self, painter, option=None, widget=None):
        self.drawLines(painter)


    def drawLines(self, p):


        p.setPen(self.pen)
        line = QtCore.QLineF(QtCore.QPointF(0,  0),
                             QtCore.QPointF(self.width,  0))
        p.drawLine(line)
        line2 = QtCore.QLineF(QtCore.QPointF(0,  self.height),  QtCore.QPointF(0,  0))
        p.drawLine(line2)

    def boundingRect(self):
        return QtCore.QRectF(0, 0,  self.width, self.height)




class View(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()
        self.resize(602, 602)
        self.scale(1, -1)



class Scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 500, 500)
        self.setBackgroundBrush(QtGui.QColor("#FFFFFF"))
        axes = Axes(self, pen=None)
        axes.setPos(30, 30)

        self.addItem(axes)
        axes.set_pen(QtGui.QPen(QtGui.QColor("darkgrey"), 1, QtCore.Qt.SolidLine))


    def on_changed_value(self, v):
        print(v)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = View()
    scene = Scene()
    main.setScene(scene)
    main.show()
    sys.exit(app.exec_())

