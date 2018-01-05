import sys
from functools import partial

from PyQt5 import QtWidgets, QtGui, QtCore



class Box(QtWidgets.QBoxLayout):
    horizontal = QtWidgets.QBoxLayout.LeftToRight = 0
    vertical = QtWidgets.QBoxLayout.TopToBottom = 2
    __box_margin = (0, 0, 0, 0)
    __box_spacing = 0
    def __init__(self, direction, parent=None,
                 margin=__box_margin, spacing=__box_spacing):
        """
        :param direction: Box._horizontal \ Box._vertical
        :param QWidget_parent: QWidget
        :param margin: поле вокруг
        :param spacing: интервал (шаг) между виджетами
        """
        super().__init__(direction, parent)
        self.setDirection(direction)
        self.setContentsMargins(*margin)
        self.setSpacing(spacing)


    def addWidget(self, QWidget, stretch=0, Qt_Alignment=None, Qt_AlignmentFlag=None, *args, **kwargs):
        if self.direction() == Box.horizontal:
            super().addWidget(QWidget, alignment=QtCore.Qt.AlignLeft)
        elif self.direction() == Box.vertical:
            super().addWidget(QWidget, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

    def add_widgets(self, *widgets, stretch=0, Qt_Alignment=None, Qt_AlignmentFlag=None):
        for w in widgets:
            self.addWidget(w, stretch, Qt_Alignment, Qt_AlignmentFlag)



class SetBtn(QtWidgets.QPushButton):
    def __init__(self, size, name=None, *__args):
        super().__init__(*__args)
        self.setObjectName(name)
        self.setFixedSize(*size)

class Button(QtWidgets.QPushButton):
    def __init__(self, name, text, checkable=False, exclusive=False):
        super().__init__()
        if text is not None:
            self.setText(text)
        self.setCheckable(checkable)
        self.setObjectName(name)
        self.setAutoExclusive(exclusive)