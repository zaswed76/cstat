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
from cstatn.log import log as lg
from cstatn import pth

import matplotlib

matplotlib.use("TkAgg")  # set the backend

import pandas as pd

import matplotlib

log = lg.log(os.path.join(pth.LOG_DIR, "plot.log"))



class Graphic:

    def __init__(self):


        self.plots = {}
        self.index_name = 0

    def set_legend(self, names):
        plt.legend(names)



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
        font = {'family': 'DejaVu Sans',
        'color':  '#022E38',
        'weight': 'normal',
        'size': 8,
        }

        ylabels=range(self.y_limit[0], self.y_limit[1]+1, 10)
        self.plots[name].set_xticklabels(time, fontdict=font)
        self.plots[name].set_yticklabels(ylabels , fontdict=font)

        title = kwargs.get("title")
        if title is not None:
            self.plots[name].set_title(title, loc='right')
        self.plots[name].set_ylim(*self.y_limit)
        if kwargs.get("grid"):

            self.plots[name].yaxis.grid(which="major",
                                        color='#BEBEBE',
                                        linestyle='dashdot',
                                        linewidth=0.5)
        dey_colors = kwargs.get("dey_colors")
        if dey_colors:
            for xtick, color in zip(self.plots[name].get_xticklabels(), dey_colors):
                xtick.set_color(color)

    def set_text(self, text):
        ymin, ymax = self.y_limit
        plt.text(0, ymax+1, text, style='italic', fontsize=8)

                 # bbox={'facecolor': 'lightgrey', 'alpha': 0.1,
                 #       'pad': 5, 'boxstyle': 'round,pad=1'}

    def pos(self, pos_str):
        xmin, xmax, ymin, ymax = plt.axis()
        pos = {}
        pos[("left-top-over")] = xmin, ymax+1
        pos[("center-top-over")] = xmax/2, ymax+1
        return pos[pos_str]

    def text(self, text, pos_str):
        pos = self.pos(pos_str)
        plt.text(*pos, text, style='italic', fontsize=8,
                 color="#5D5D5D")

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

    def clear(self):
        plt.cla()

