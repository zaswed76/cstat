

import sqlite3 as sql
import os

import pandas as pd



pth = r"D:\0SYNC\python_projects\cstat\programm\data\data.sql"
# pth = r"D:\0SYNC\python_projects\cstat\programm\data\plot.png"
if not os.path.isfile(pth):
    print("not ex file")

else:
    connect = sql.connect(pth)
    query = "SELECT * FROM table_club"
    print(pd.read_sql_query(query, connect))




