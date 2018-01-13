import sqlite3
import pandas as pd

class Keeper():
    def __init__(self, path):
        self.path = path

    def open_connect(self):
        self.connect = sqlite3.connect(self.path)

    def open_cursor(self):
        self.cursor = self.connect.cursor()

    def sample_range_date_time(self, club, start, end, step=1):
        self.open_connect()
        query = "SELECT * FROM club WHERE (club = ?) AND (data_time BETWEEN ? AND ?)"
        df = pd.read_sql_query(query, self.connect, params=(club, start, end))
        res = df[df["mminute"]==0]
        return res
