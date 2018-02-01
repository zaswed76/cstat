import datetime
import os
import sqlite3
from collections import Counter

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


def get_data_every_time(data: pd.DataFrame, time_category: str) -> pd.DataFrame:
    # todo переписать

    """
    берёт данные по каждому часу , вычисляет среднее арифм.
    в колонках - m_col,
    и возвращает pd.DataFrame с той же структурой колонок
    и колличетсвом сттрок равным hour_lst
    :param data:
    :param time_category: имя колонки data (часы или даты )
    если часы то считает усреднённые данные за каждый час
    если даты то усреднённые данные за день
    :return:
    """
    m_col = ['taken', 'free',
             'guest', 'resident', 'admin', 'workers', 'school',
             'visitor']
    list_res = []
    hour_lst = data[time_category].unique()
    club = data["club"][0]
    date = data["dt"][0]
    for h in hour_lst:
        lst = [date, pd.NaT, h, 0, club, pd.NaT]
        ser = data[data[time_category].between(h, h)]
        lst.extend(ser[m_col].mean())
        list_res.append(lst)
    res = pd.DataFrame(list_res, columns=data.columns)
    return res


def get_data_every_day(data: pd.DataFrame, time_category: str, controller_data) -> pd.DataFrame:
    m_col = ['taken', 'free',
             'guest', 'resident', 'admin', 'workers', 'school',
             'visitor']
    list_res = []
    data["data_time"] = pd.to_datetime(data["data_time"])
    time_lst = list(map(pd.Timestamp, data["data_time"].unique()))
    print(time_lst[0].date())
    print(time_lst[-1].date())
    start_d = pd.Timestamp.combine(time_lst[0].date(), controller_data["time_start"])
    end_d = pd.Timestamp.combine(time_lst[-1].date(), controller_data["time_end"])
    time_stamp = pd.date_range(start_d, end_d)
    for s in time_stamp:
        lst = [s]
        start_date = s
        end_d = s + datetime.timedelta(days=1)
        end_date = datetime.datetime.combine(end_d.date(), controller_data["time_end"])
        ser = data[data["data_time"].between(start_date, end_date)]
        lst.extend(ser[m_col].mean())
        list_res.append(lst)

    res = pd.DataFrame(list_res, columns=["data_time"]+m_col)
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
        # dict(minute=count comp) колличество пк каждые n минут
        counter = Counter(one_hour_data["mminute"].tolist())
        mean = sum(counter.values()) / count_measurements_hour
        res[h] = round(mean, 2)
    return pd.DataFrame(list(res.items()), columns=["mhour", "mean"])


def measurements_hour(data):
    """

    :param data:
    :return: int колличество замеров в час
    """
    # mh = data[data["mhour"]>9]["mminute"].unique()
    # mh.sort()
    # TODO SDFG
    return 12


def get_mean_people(visitor, r=0):
    lenght = len(visitor)
    s = sum(visitor)
    return round(s / lenght)


def get_mean_load(avis, max, r=0):
    r = (avis / max) * 100
    return round(r, 1)


def data_period_time(date, period_time, d, period_column):
    """

    :param date: date < datetime
    :param period_time: list < str ['13:30','22:00']
    :param d: pd.DataFrame
    :param period_column: column of pd.DataFrame < str
    :return:
    """
    st, end = get_datetime_format(date, period_time)
    return d[(d[period_column] > st) & (d[period_column] < end)]


def get_datetime_format(date, time):
    """

    :param date: date < datetime
    :param time: list < str ['13:30','22:00']
    :return: (datetime, datetime)
    """
    st = time[0].split(":")
    end = time[1].split(":")
    time_st = datetime.datetime.strptime(
        '{}:{}'.format(*st), '%H:%M').time()
    time_end = datetime.datetime.strptime(
        '{}:{}'.format(*end), '%H:%M').time()
    date_st = datetime.datetime.combine(date,
                                        time_st).strftime(
        "%Y-%m-%d %H:%M:%S")
    date_end = datetime.datetime.combine(date,
                                         time_end).strftime(
        "%Y-%m-%d %H:%M:%S")
    return date_st, date_end


def get_percentage_ratio(data, column_1, column_2,
                         ndigits=1):
    """
    вычисляет процентное отношение 2-й колонки к 1-й
    значение колонок должно былть числовыми значениями
    :param data: pd.DataFrame
    :param column_1: str имя первой колонки
    :param column_2: str имя колонки
    :param ndigits: колличество знаков после запятой
    :return: float
    """
    greater = data[column_1].sum()
    lower = data[column_2].sum()
    if greater:
        r = percentile(greater, lower)
    else:
        r = 0
    return round(r, ndigits)


def percentile(number1, number2):
    return (number2/number1) * 100

def time_occupied(data, column, max, measurements, ndigits=1):
    """

    :param data:
    :param column:
    :param max:
    :param measurements:
    :param ndigits:
    сколько процентов времени от measurements значения column == max
    :return: float
    """

    if max > 0:
        number1 = data[data[column] >= float(max)-0.5][column].size
    else:
        number1 = data[data[column] <= float(max)+0.5][column].size
    measurements = data[column].size
    return round(percentile(measurements, number1), ndigits)


def date_colors(dates, weekend_days, week_color, work_color):
    colors  = []
    for d in dates:
        if d.dayofweek in weekend_days:
           colors.append(week_color)
        else:
            colors.append(work_color)
    return colors

