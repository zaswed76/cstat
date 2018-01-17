import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, \
    QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import os
from programm.log import log as lg
from programm import pth

import matplotlib

matplotlib.use("TkAgg")  # set the backend

import pandas as pd

import matplotlib

log = lg.log(os.path.join(pth.LOG_DIR, "plot.log"))


class Graphic:
    def __init__(self):
        self.plots = {}
        self.index_name = 0

    def set_legend(self, names, bg=None, color_matching=False,
                   alpha=1.0):
        plots = []
        names = []
        colors = []
        for n, p in self.plots.items():
            plots.append(p)
            names.append(n)
            colors.append(p.get_facecolor())
        legend = plt.legend(names, shadow=False, fancybox=True)
        frame = legend.get_frame()
        frame.set_alpha(alpha)
        frame.set_linewidth(0.5)
        frame.set_edgecolor('black')
        if bg is not None:
            frame.set_facecolor("black")
        if color_matching:
            for color, text in zip(colors, legend.get_texts()):
                text.set_color(color)

    def show(self):
        plt.show()

    def set_y_limit(self, st, end):
        log.debug("{}-{}".format(st, end))

    def plot(self, time, visitor, **kwargs):
        try:
            name = kwargs["name"]
        except KeyError:
            name = self.index_name
            self.index_name += 1
        freq_series = pd.Series.from_array(visitor)
        self.plots[name] = freq_series.plot(kind='bar',
                                            color=kwargs.get("color",
                                                             "green"),
                                            width=kwargs.get("width",
                                                             0.9))
        self.plots[name].set_xticklabels(time)
        title = kwargs.get("title")
        if title is not None:
            self.plots[name].set_title(title)
        self.plots[name].set_ylim(*kwargs.get("limit", (0, 60)))

    def add_pc_max(self, pc_max, length):

        if pc_max is not None:
            plt.plot([0, length - 1],
                                  [pc_max, pc_max],
                                  color="#E988A9", linewidth=0.8)
            plt.annotate('pc max', xy=(length/2, pc_max+1), color="#1B97B9")

    def set_bg(self, color="lightgrey"):
        list(self.plots.values())[-1].set_facecolor(color)

    def close(self):
        plt.clf()
        plt.cla()
        plt.close()

    def save_from_file(self):
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(9, 6)
        margins = {  #     vvv margin in inches
        "left"   :     0.07,
        "bottom" :     0.12,
        "right"  : 0.98,
        "top"    : 0.94
}
        print(margins)
        fig.subplots_adjust(**margins)
        fig.savefig(pth.PLOT_PATH, dpi=96)

    def set_grid(self, *args):
        plt.grid()
