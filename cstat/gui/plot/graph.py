import pandas as pd
import matplotlib.pyplot as plt
import matplotlib


class Graph:
    def __init__(self, times, human, x_lb, y_lb, width=0.5, title="", max=40):

        self.max = max
        self.title = title
        self.width = width
        self.y_lb = y_lb
        self.x_lb = x_lb
        self.human = human
        self.times = times
        # self.create_plot()

    def create_plot(self, human, color=None):
        if color is None:
            color = "green"
        else: color = color
        freq_series = pd.Series.from_array(human)
        self.ax = freq_series.plot(kind='bar', width=self.width, color=color)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_lb)
        self.ax.set_ylabel(self.y_lb)
        self.ax.set_xticklabels(self.times)

        plt.ylim([0, self.max])
        rects = self.ax.patches

        # for rect, label in zip(rects, human):
        #     height = rect.get_height()
        #     self.ax.text(rect.get_x() + rect.get_width() / 2,
        #                  height + 0.4,
        #                  label, ha='center', va='bottom')
        #     if len(self.times) < 24:
        #         size = 10
        #     else:
        #         size = 8
        #
        #     font = {'family': 'Calibri',
        #             'size': size}
        #
        #
        #     matplotlib.rc('font', **font)

    def create_plot2(self, human, color=None):
        if color is None:
            color = "green"
        else: color = color
        freq_series = pd.Series.from_array(human)
        self.ax = freq_series.plot(kind='bar', width=self.width, color=color)
        self.ax.set_title(self.title)
        self.ax.set_xlabel(self.x_lb)
        self.ax.set_ylabel(self.y_lb)
        self.ax.set_xticklabels(self.times)

        plt.ylim([0, self.max])
        rects = self.ax.patches

        # for rect, label in zip(rects, human):
        #     height = rect.get_height()
        #     self.ax.text(rect.get_x() + rect.get_width() / 2,
        #                  0,
        #                  label, ha='center', va='bottom')
        #     if len(self.times) < 24:
        #         size = 10
        #     else:
        #         size = 8
        #
        #     font = {'family': 'Calibri',
        #             'size': size}
        #
        #
        #     matplotlib.rc('font', **font)


    def show(self):
        plt.show()
        plt.clf()
        plt.cla()
        plt.close()

    def save(self, path):
        plt.savefig(path)
        plt.clf()
        plt.cla()
        plt.close()


if __name__ == '__main__':
    mans = [6, 7, 18, 19, 10, 15, 17, 12, 16, 17, 17, 23, 27,
            28, 17, 18, 19, 10, 15, 17, 12, 26, 17, 13]

    mans2 = [0, 0, 0, 0, 0, 1, 17, 12, 16, 7, 3, 7, 8,
            6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    x_labels0 = ["{number:02}".format(number=x) for x in
                 list(range(9, 25))]
    x_labels1 = ["{number:02}".format(number=x) for x in
                 list(range(1, 10))]
    times = []
    times.extend(x_labels0)
    times.extend(x_labels1)
    gr = Graph(times, mans, "время", "человек", width=0.8,
               title="Lesnoy")
    gr.create_plot(mans, color="green")
    gr.create_plot2(mans2, color="#F8EF3E")
    gr.show()

