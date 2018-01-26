
import sys
from PyQt5 import QtWidgets

def choose_db_dialog(last_dir=None):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "",
                                                            last_dir, "",
                                                            options=options)
        return fileName

def save_file_dialog(last_dir=None, ext=".png"):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, "",
                                                            last_dir, ext,
                                                            options=options)
        return fileName

