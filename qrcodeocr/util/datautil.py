# -*- coding: utf-8 -*-

import pandas as pd
from dateutil.relativedelta import relativedelta


def inner_join_dataframes(df_list):
    '''
    Inner join of data frames
    :param df_list: data frame list
    :return:
    '''
    res = pd.concat(df_list, axis=1, join='inner')
    return res


def outer_join_dataframes(df_list):
    '''
    Outer join of data frames
    :param df_list: data frame list
    :return:
    '''
    res = pd.concat(df_list, axis=1, join='outer')
    return res


def filling_missing_price(df, value=None):
    '''
    filling missing price in data frame
    :param df: data frame
    :param value: value to replace missing fields
    :return:
    '''
    if value == None:
        res = df.fillna(method='pad')  # filling missing data forward.  'pad': forward; 'bfill': backward,
    else:
        res = df.fillna(value)
    return res


def get_months_diff(date1, date2):
    '''
    return date difference in months
    :param date1: target date
    :param date2: referencing date
    :return:
    '''
    rd = relativedelta(date1, date2)
    return (12 * rd.years + rd.months) + 1
