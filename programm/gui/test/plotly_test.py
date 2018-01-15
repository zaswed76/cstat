
import pyqtgraph as pg
import numpy as np
from PyQt5 import QtWidgets as QtGui  # (the example applies equally well to PySide)


## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()

## Create some widgets to be placed inside
btn = QtGui.QPushButton('press me')
text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()
plot = pg.PlotWidget()

x = np.random.normal(size=1000)
y = np.random.normal(size=1000)
# plot.plot(x, y, pen=None, symbol='o')  ## setting pen=None disables line drawing

b = pg.BarGraphItem(x=[1, 2, 3], height=[3, 4, 5], width=0.9, brush='g')
plot.setBackground("#555555")


plot.addItem(b)



## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

## Add widgets to the layout in their proper positions
layout.addWidget(btn, 0, 0)   # button goes in upper-left
layout.addWidget(text, 1, 0)   # text edit goes in middle-left
layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
layout.addWidget(plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows

## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()