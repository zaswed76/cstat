
import sys
from PyQt5 import QtWidgets, QtGui, QtCore


class SliderDiapasonWidget(QtWidgets.QFrame):
    def __init__(self, orientation, parent=None,
                 mark_names=None, *args, **kwargs):

        super().__init__(parent, *args, **kwargs)
        # self.setStyle(QtWidgets.QStyle(QtWidgets.QStyle.CC_Slider))
        if mark_names is not None:
            self.mark_names = mark_names

        self.box = QtWidgets.QVBoxLayout(self)
        self.slider_box = QtWidgets.QHBoxLayout(self)
        d = len(mark_names[0])//2
        de = len(mark_names[-1])//2
        self.slider_box.setContentsMargins(0, 0, 0, 0)
        self.box.setContentsMargins(10, 10, 10, 10)
        self.label_box = QtWidgets.QHBoxLayout()
        self.label_box.setContentsMargins(0, 0, 0, 0)
        self.box.addLayout(self.slider_box)
        self.box.addLayout(self.label_box)
        self.labels = {}
        self.slider = QtWidgets.QSlider()
        self.slider.setStyleSheet(""" QSlider::handle:horizontal {
     background: #0da9ff;
     border: 1px solid #2a06a9;
     width: 18px;
     margin: -2px 0; /* рукоятка располагается по умолчанию в прямоугольнике содержимого бороздки. Расширяется наружу от бороздки */
     border-radius: 2px;
     
     

 }""")

        for m in self.mark_names:
            self.labels[m] = QtWidgets.QLabel(m)

        self.slider.setOrientation(orientation)

        self.slider.setRange(0, len(self.labels)-1)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)


        self.slider_box.addWidget(self.slider)
        self.label_box.setSpacing(50)

        labels = list(self.labels.values())
        s = labels[0]
        m = labels[1:len(labels)-1]
        e = labels[-1]
        self.label_box.addWidget(s, alignment=QtCore.Qt.AlignLeft)
        for n, lb in enumerate(m):
            self.label_box.addWidget(lb, alignment=QtCore.Qt.AlignCenter)
        self.label_box.addWidget(e, alignment=QtCore.Qt.AlignRight)







if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('./etc/{0}.qss'.format('style'), "r").read())
    main = SliderDiapasonWidget(QtCore.Qt.Horizontal, mark_names=["10 мин", "30 мин", "1  час", "   1 д"])
    # main.setStyle(QtWidgets.QStyleFactory.create())
    main.show()
    sys.exit(app.exec_())




