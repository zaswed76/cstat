import datetime
import os
import sqlite3
from collections import Counter
import pandas as pd
import numpy as np
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

def mean_hourly_data(h_hours, count_measurements_hour, data):
    """

    :param data: pd.DataFrame
    :param h_hours: pd.Series
    :param count_measurements_hour: int
    :return: pd.DataFrame columns=["mhour", "mean"]
    """

    res = {}
    for h in h_hours:
        one_hour_data = data[data["mhour"].between(h, h)]
        print(one_hour_data[["mhour", "mminute", "ncomp"]])
        print("-------------")
        # dict(minute=count comp) колличество пк каждые n минут
        counter = Counter(one_hour_data["mminute"].tolist())
        mean = sum(counter.values())/count_measurements_hour
        res[h] = round(mean, 2)
    return pd.DataFrame(list(res.items()), columns=["mhour", "mean"])


def measurements_hour(data):
    """

    :param data:
    :return: int
    """
    # mh = data[data["mhour"]>9]["mminute"].unique()
    # mh.sort()
    # TODO SDFG
    return 12
