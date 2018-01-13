import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import random

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=110):
        fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.fig = fig
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)




    def plot(self, time, visitor, **kwargs):
        self.fig.clear()
        self.ax = self.figure.add_subplot(111)

        self.plots_ = self.ax.bar(time, visitor,
                                       color=kwargs.get("color", "green"),
                                       width=kwargs.get("width", 0.8),
                                       alpha=kwargs.get("alpha", 1.0))

        self.draw()