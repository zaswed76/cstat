import sys
from PyQt5 import QtWidgets, QtGui, QtCore


class SliderDiapasonWidget(QtWidgets.QFrame):
    def __init__(self, orientation, parent=None,
                 mark_names=None, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)
        if mark_names is not None:
            self.mark_names = mark_names

        self.box = QtWidgets.QVBoxLayout(self)
        self.slider_box = QtWidgets.QHBoxLayout(self)
        d = len(mark_names[0]) // 2
        de = len(mark_names[-1]) // 2
        self.slider_box.setContentsMargins(0, 0, 0, 0)
        self.box.setContentsMargins(10, 10, 10, 10)
        self.label_box = QtWidgets.QHBoxLayout()
        self.label_box.setContentsMargins(0, 0, 0, 0)
        self.box.addLayout(self.slider_box)
        self.box.addLayout(self.label_box)
        self.labels = []
        self.slider = QtWidgets.QSlider()


        for m in self.mark_names:
            self.labels.append(QtWidgets.QLabel(m))

        self.slider.setOrientation(orientation)

        self.slider.setRange(0, len(self.labels) - 1)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        self.slider_box.addWidget(self.slider)
        self.label_box.setSpacing(2)

        labels = self.labels
        s = labels[0]
        m = labels[1:len(labels) - 1]
        e = labels[-1]
        self.label_box.addWidget(s, alignment=QtCore.Qt.AlignLeft)
        for n, lb in enumerate(m):
            self.label_box.addWidget(lb,
                                     alignment=QtCore.Qt.AlignCenter)
        self.label_box.addWidget(e, alignment=QtCore.Qt.AlignRight)

        self.slider.valueChanged.connect(self.diapason_change)
        self.diapason_change()

    def diapason_change(self):
        for n, l in enumerate(self.labels):
            if n == self.slider.value():

                l.setStyleSheet(
        """ QLabel{
            color: #09848f;
            border: 1px solid #07acff;
            border-radius: 4px;
            }
            """)
            else:
                l.setStyleSheet(
        """ QLabel{
            color: #6b6b6b;
            }
            """)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = SliderDiapasonWidget(QtCore.Qt.Horizontal,
                                mark_names=["10 м", "30 м",
                                            "1  ч", "   1 д"])
    # main.setStyle(QtWidgets.QStyleFactory.create())
    main.show()
    sys.exit(app.exec_())
