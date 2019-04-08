"""read_write_data.py: functions for read, write data"""

__author__ = "Raymond Lee"
__copyright__ = "Copyright 2017, Planet Earth"

import json

import pandas as pd
import requests
from qrcodeocr.common import configure
from mosql.util import raw
from pandas import DataFrame
from qrcodeocr.util import utility


# from SourceCode.Old.PG_mosql import ttld_jim
# from utility import fetchall


def read_csv(filepath):
    return pd.read_csv(filepath)


def read_csv_by_list(filepath, list):
    data_frames = {}
    file_type = '.csv'
    for filename in list:
        fn = filepath + '/' + filename + file_type
        data_frames[filename] = pd.read_csv(fn)

    return data_frames


def read_sql_query(sql, engine):
    return pd.read_sql_query(sql, engine)


def get_fund_list(db_name):
    sqlstr = "select _id from list_13"
    items = utility.fetchall(db_name, sqlstr)
    # print items

    amap = []
    for item in items:
        amap.append(item[0])

    return amap


def get_fund_nav(mfund_list, start_date, end_date, limit_n):
    kk = 0
    symbol_position = {}
    symbol_data = {}
    comb_index = None
    new_mfund_list = []
    chinese_name = []

    # print ('mfund_list=', mfund_list)

    for s in mfund_list:

        y = utility.ttld_jim.get_dao('fund').select('ff_nav', where={'_id': s, 'da >=': start_date, 'da <=': end_date},
                                                    columns=raw(
                                                        'to_char(da, \'YYYY-MM-DD\') da, fund_chinese_name, nav'),
                                                    order_by='da asc', limit=5000000)

        if len(y) >= limit_n:
            new_mfund_list.append(s)
            da_list = []
            price_list = []
            for dt in y:
                da_list.append(dt['da'])
                price_list.append(dt['nav'])

            data_bars = DataFrame(price_list, index=da_list, columns=['nav'])
            data_bars.index.names = ['date']

            data_bars.index = pd.to_datetime(data_bars.index)

            symbol_data[s] = data_bars
            kk = kk + 1
            print(kk)
            print(len(y))

            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = symbol_data[s].index
            else:
                comb_index.union(symbol_data[s].index)

    for s in new_mfund_list:
        c_name = utility.ttld_jim.get_dao('fund').select('ff_nav', where={'_id': s}, columns=raw('fund_chinese_name'),
                                                         limit=5000000)[0]
        symbol_data[s] = symbol_data[s].reindex(
            index=comb_index, method='pad'
        )

    return symbol_data


def write_to_txt_file(path, text_string):
    file = open(path, "a")
    file.write(text_string)
    file.close()

    return


def restful_api_request(url, type, str=''):
    auth_token = configure.auth_token
    if type == 'GET' and str == '':
        resp = requests.get(url, headers={'Authorization': auth_token})
    elif type == 'GET':
        resp = requests.get(url, headers={'Authorization': auth_token}, params=str)

    elif type == 'POST':
        resp = 'To-be'
    else:
        resp = 'To-be'

    if resp.status_code != 200:
        res = "Error raised:"
    else:
        res = json.dumps(resp.json())
        print("Restful api result:\n")
        print(res)

    return res


if __name__ == "__main__":
    # res = restful_api_request(const.api_fund_list, 'GET')
    qStr = {'howfundId': 'howF7'}
    res = restful_api_request(configure.api_fund_detail, 'GET', qStr)
    print('--out main --')
