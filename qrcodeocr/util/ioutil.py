# -*- coding: utf-8 -*-

import pandas as pd


def read_csv_by_list(filepath, list):
    dataframes = {}
    file_type = '.csv'
    for filename in list:
        fn = filepath + '/' + filename + file_type
        dataframes[filename] = pd.read_csv(fn)
    return dataframes


if __name__ == '__main__':
    rs = read_csv_by_list("../data", ['howF1294', 'howF4002'])
    print(rs)
