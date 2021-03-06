import datetime
import os
import sys
import sqlite3
from collections import Counter

import pandas as pd

from cstatn import pth
from cstatn.log import log as lg
from cstatn.sql import sql_keeper as keeper

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


def get_data_every_time(data: pd.DataFrame,
                        time_category: str,
                        list_work_hours) -> pd.DataFrame:
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

    club = data["club"][0]
    date = data["dt"][0]
    for h in list_work_hours:
        lst = [date, pd.NaT, h, 0, club, pd.NaT]
        ser = data[data[time_category].between(h, h)]
        measur = ser["mminute"].size

        lst.extend(ser[m_col].mean())
        lst.append(measur)
        list_res.append(lst)
    col = data.columns.tolist()
    col.append("measur")
    res = pd.DataFrame(list_res, columns=col)
    return res


def get_data_every_day(data, time_category, start_end_dates, mean_columns=None):
    res = []
    columns = ["data_time"] + mean_columns
    columns.append("measur")
    columns.append("measur_hours")
    for start, end, in start_end_dates:
        one_day_data = data[data["data_time"].between(start, end)]
        count_measurements_hour = one_day_data["mhour"].unique().size
        loc = [start]
        if count_measurements_hour > 12:
            mean = one_day_data[mean_columns].mean().tolist()
        else:
            mean = [0]
        loc.extend(mean)
        loc.append(one_day_data["data_time"].size)
        loc.append(count_measurements_hour)
        res.append(loc)
    df = pd.DataFrame(res, columns=columns)
    return df


def get_data_table_every_day(data, time_category, start_end_dates, working_club_hours,
                             measur_every_day,
                             measur_hours,
                             mean_columns=None):
    res = []
    columns = ["data_time"] + mean_columns
    for start, end, in start_end_dates:
        one_day_data = data[data["data_time"].between(start, end)]
        # print(one_day_data)
        # print("--------------")
        real_hours = one_day_data["mhour"].unique().size
        # print(real_hours)
        # print("--------------")

        if real_hours < working_club_hours:
            size_hours = real_hours
        else:
            size_hours = working_club_hours

        loc = [start]
        if size_hours > 12:
            measur = measur_every_day[measur_every_day["data_time"] == start]["measur"]
            counter = one_day_data["mminute"].value_counts()
            mean = [sum(counter.tolist()) / measur]
        else:
            mean = [0]
        loc.extend(mean)
        res.append(loc)
    df = pd.DataFrame(res, columns=columns)
    print(df)
    print("#############################################")
    return df


def get_start_end_dates(data, start_time, end_time, period=1):
    st = datetime.datetime.strptime(start_time, "%H:%M").time()
    endt = datetime.datetime.strptime(end_time, "%H:%M").time()
    res = []
    stamp = get_time_stamp(data, st, endt)
    for start_date in stamp:
        next_date = start_date + datetime.timedelta(days=period)
        end_date = datetime.datetime.combine(next_date.date(), endt)
        res.append((start_date, end_date))
    return res


def get_time_stamp(data, start_time, end_time):
    time_lst = list(map(pd.Timestamp, data["data_time"].unique()))
    start_d = pd.Timestamp.combine(time_lst[0].date(), start_time)
    end_d = pd.Timestamp.combine(
        time_lst[-1].date(), end_time)
    return pd.date_range(start_d, end_d)


def mean_hourly_data(h_hours, mhour_measur, data):
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
        measur = mhour_measur[mhour_measur["mhour"] == h]["measur"].tolist()[0]

        mean = sum(counter.values()) / measur

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


def list_work_hours(data: pd.DataFrame, work_time: dict):
    sdate_time = data["data_time"].min()

    edate_time = data["data_time"].max()
    sdate = sdate_time.date()
    edate = edate_time.date()

    if edate - sdate > datetime.timedelta(days=0):
        etime = datetime.datetime.strptime(work_time["end"], "%H:%M").time()
    else:
        etime = edate_time.time()

    stime = datetime.datetime.strptime(work_time["start"], "%H:%M").time()

    start_date = datetime.datetime.combine(sdate, stime)
    end_date = datetime.datetime.combine(edate, etime)

    hour_list = data[data["data_time"].between(start_date, end_date)]["mhour"].unique()
    return hour_list


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
    return (number2 / number1) * 100


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
    # print(data)

    if max > 0:
        number1 = data[data[column] >= float(max) - 0.5][column].size
    else:
        number1 = data[data[column] <= float(max) + 0.5][column].size
    measurements = data[column].size
    return round(percentile(measurements, number1), ndigits)


def date_colors(dates, weekend_days, week_color, work_color):
    colors = []
    for d in dates:
        if d.dayofweek in weekend_days:
            colors.append(week_color)
        else:
            colors.append(work_color)
    return colors


def measurements_in_day(data, start, end):
    one_day_data = data[data["data_time"].between(start, end)]
    return one_day_data["mhour"].unique().size


def measurements(data, ndigits=1):
    """

    :param data: list < int
    :param ndigits: int округлить до
    :return: среднее арифметическое списка чисел если число не равно 0
    """
    all_lst = [x for x in data if x > 0]
    return round(sum(all_lst) / len(all_lst), 2)
