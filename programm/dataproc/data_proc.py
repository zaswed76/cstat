import datetime
import os
import sqlite3
import pandas as pd
from programm import pth
from programm.log import log as lg
from programm.sql import sql_keeper as keeper

log = lg.log(os.path.join(pth.LOG_DIR, "data_proc.log"))


def get_data(table_name=None, controller_data=None,
             db_path=None, club_name=None) -> pd.DataFrame:
    """

    :param table_name: str
    :param controller_data: dict
    :param db_path: str
    :param club_name: str
    :return: pd.DataFrame
    """
    kp = keeper.Keeper(db_path)
    start = datetime.datetime.combine(
        controller_data["date_start"],
        controller_data["time_start"])
    end = datetime.datetime.combine(controller_data["date_end"],
                                    controller_data["time_end"])
    try:
        data = kp.sample_range_date_time(table_name, club_name, start,
                                         end)
    except pd.io.sql.DatabaseError as er:
        log.error(er)
        res = None
    except sqlite3.OperationalError as er:
        log.error(er)
        res = None
    else:
        res = data
    return res

def average_hourly_values(data, columns):
    list_res = []

    hour_lst = data["mhour"].unique()
    club = data["club"]
    date = data["dt"]

    for h in hour_lst:
        # lst = [date, h, 0, club]
        ser = data[data["mhour"].between(h, h)]
        print(ser)
        print("----------------------")
    #     lst.extend(ser[columns].mean())
    #     list_res.append(lst)
    # res = pd.DataFrame(list_res, columns=columns)
