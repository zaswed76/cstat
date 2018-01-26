import sqlite3
import pandas as pd

def filter_60_min(data: pd.DataFrame) -> pd.DataFrame:
    return data[data["mminute"]==0]

def filter_30_min(data: pd.DataFrame) -> pd.DataFrame:
    pass

def filter_10_min(data: pd.DataFrame) -> pd.DataFrame:
    pass

class Keeper():

    def __init__(self, path):
        self.path = path


    def open_connect(self):
        # print(self.path, "path")
        self.connect = sqlite3.connect(self.path)

    def open_cursor(self):
        self.cursor = self.connect.cursor()

    def sample_range_date_time(self, club, start, end, step=1):
        self.open_connect()
        query = "SELECT * FROM club WHERE (club = ?) AND (data_time BETWEEN ? AND ?)"
        df = pd.read_sql_query(query, self.connect, params=(club, start, end))
        return df




    def sample_range_date_time_table(self, club, start, end, step=0):
        self.open_connect()
        query = "SELECT * FROM club_tab WHERE (club = ?) AND (data_time BETWEEN ? AND ?)"
        df = pd.read_sql_query(query, self.connect, params=(club, start, end))
        if step:
            print(9999999999999999999999)
            res = df[df["mminute"]==0]
        else:
            res = df
        return {"step_data": res, "all_data": df}