
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import (QApplication, QGraphicsTextItem,
                             QGraphicsRectItem, QGraphicsScene,
QGraphicsView)


class TextItem(QGraphicsTextItem):
    selectedChange = pyqtSignal(str)

    def __init__(self, parent=None, scene=None):
        super(TextItem, self).__init__(parent, scene)
        self.setPlainText('test2')

    def mousePressEvent(self, event):
        self.selectedChange.emit('TextItem')
        super(TextItem, self).mousePressEvent(event)


class RectItem(QGraphicsRectItem):
    selectedChange = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RectItem, self).__init__(-30, -30, 30, 30, parent)
        pen = QPen(Qt.red, 2, Qt.SolidLine,
                   Qt.RoundCap, Qt.RoundJoin)
        self.setPen(pen)

    def mousePressEvent(self, event):
        self.selectedChange.emit('RectItem')
        super(RectItem, self).mousePressEvent(event)


def message(string):
    print(string)


app = QApplication(sys.argv)
scene = QGraphicsScene()

text = TextItem()
text.selectedChange.connect(message)
scene.addItem(text)

rect = RectItem()
rect.selectedChange.connect(message)
scene.addItem(rect)

view = QGraphicsView(scene)
view.show()

sys.exit(app.exec_())