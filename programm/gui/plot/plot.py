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
        self.y_limit = kwargs.get("y_limit", (0, 60))
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
            self.plots[name].set_title(title, loc='right')
        self.plots[name].set_ylim(*self.y_limit)
        if kwargs.get("grid"):

            self.plots[name].yaxis.grid(which="major",
                                        color='#BEBEBE',
                                        linestyle='dashdot',
                                        linewidth=0.5)

    def set_text(self, text):
        ymin, ymax = self.y_limit
        plt.text(0, ymax+1, text, style='italic',
                 bbox={'facecolor': 'lightgrey', 'alpha': 0.1,
                       'pad': 5, 'boxstyle': 'round,pad=1'})

    def add_horizontal_line(self, height, length, color="r", text=""):

        if height:
            plt.plot([0, length - 1],
                     [height, height],
                     color=color, linewidth=0.8)
            plt.annotate(text, xy=(0, height + 1),
                         color=color)

    def set_bg(self, color="lightgrey"):
        list(self.plots.values())[-1].set_facecolor(color)

    def close(self):
        plt.clf()
        plt.cla()
        plt.close()

    def save_from_file(self, path=""):
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches(8, 5)
        margins = {
            "left": 0.07,
            "bottom": 0.09,
            "right": 0.98,
            "top": 0.90
        }
        fig.subplots_adjust(**margins)
        if path:
            p = path
        else:
            p = pth.PLOT_PATH
        fig.savefig(p, dpi=96)

        # def set_grid(self, *args):
        #     plt.yaxis.grid()(True, which='both')
