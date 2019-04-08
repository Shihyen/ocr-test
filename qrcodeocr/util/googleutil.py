# -*- coding: utf-8 -*-
import json
import logging
import time
import urllib
import urllib.parse
import urllib.request

import pandas as pd
from qrcodeocr.common import configure
from pandas import DataFrame
from qrcodeocr.util import utility

logger = logging.getLogger(__name__)


class GoogleUtil:

    # dictionary mapping for short names
    googleFinanceKeyToFullName = {
        't': 'ticker',
        'l': 'quote',
        'lt_dts': 'LastTradeDateTime',
        'c': 'change',
        'cp': 'changePercent',
        'pcls_fix': 'prevClose'
    }

    def __init__(self):

        self.logEnabled = configure.db_logEnabled

    def log(self, st):

        if (self.logEnabled):
            timediff = int((time.time() - st) * 1000)

            logger.info('[GoogleFinance] Time(ms):[%s]', timediff)

    def buildUrl(self, symbols):
        """
        build url for request
        :param symbols:
        :return:
        """
        symbol_list = ','.join([symbol for symbol in symbols])
        # a deprecated but still active & correct api
        return 'http://finance.google.com/finance/info?client=ig&q=' \
               + symbol_list

    def replaceKeys(self, quotes):
        """
        replace short names for meaningful names
        :param quotes:
        :return:
        """
        quotesWithReadableKey = []
        for q in quotes:
            qReadableKey = {}
            for k in self.googleFinanceKeyToFullName:
                if k in q:
                    qReadableKey[self.googleFinanceKeyToFullName[k]] = q[k]
            quotesWithReadableKey.append(qReadableKey)
        return quotesWithReadableKey

    def getQuotes(self, symbol_df):
        """
        retrieve quote for symbols
        :param symbol_df:
        :return:
        """
        st = time.time()

        result = []
        try:

            url = self.buildUrl(list(symbol_df['symbol']))
            content = urllib.request.urlopen(url).read().decode('utf-8')
            content = content[3:]
            # result data as dictionary
            data_dic = json.loads(content)
            # replace short names
            data_dic = self.replaceKeys(data_dic)

            df = DataFrame(data_dic)
            df.set_index('ticker', inplace=True)
            df['tradeDate'] = [utility.format_date(d, '%Y-%m-%dT%H:%M:%SZ') for d in df['LastTradeDateTime']]
            df['local'] = [utility.format_24time(d, '%Y-%m-%dT%H:%M:%SZ') for d in df['LastTradeDateTime']]
            df['quote'] = [float(f.replace(',','')) for f in df['quote']]
            df['change'] = [float(f) for f in df['change']]
            df['changePercent'] = [utility.convert_percent_to_float(f) for f in df['changePercent']]

            df = df.join(symbol_df)

            # calcuate YTDROI from ytd field
            df['YTDROI'] = [utility.format_float(f) for f in ((df['quote'] - df['ytd']) / df['ytd'])]

            df.sort_values(['order'], inplace=True)

        except Exception as e:
            logger.error("google gQ read_sql exception: " + str(e))
            return None
        self.log(st)

        return df


    def get_historical(self, symbol, startdate, enddate):
        """
        retrieve historical data by symbol, startdate and enddate
        :param symbol:
        :param startdate:
        :param enddate:
        :return:
        """

        url = 'http://www.google.com/finance/historical?q=%s&startdate=%s&enddate=%s&output=csv' % (symbol, startdate, enddate)
        df = pd.read_csv(url)

        return df

    def get_YTD(self, symbol):
        """
        retrieve YTD price for symbol
        :param symbol:
        :return:
        """
        startdate, enddate = utility.get_ytd_for_google()
        url = 'http://www.google.com/finance/historical?q=%s&startdate=%s&enddate=%s&output=csv' % (symbol, startdate, enddate)
        try:
            df = pd.read_csv(url)
            df['symbol'] = symbol
            df.set_index(['symbol'], inplace=True)
            df = df.head(1)['Close']
        except Exception as e:
            logger.debug(e)
            return None
        return df

    def get_all_YTDs(self, symbol_df):
        st = time.time()


        try:
            _df_list = []
            for symbol in list(symbol_df['symbol']):
                # print(symbol)
                df = self.get_YTD( symbol)
                # print(df)
                if (df is not None):
                    _df_list.append(df)

            # print(_df_list)
            _dfs = pd.concat(_df_list, axis=0, join='outer')
            print(_dfs)
            return _dfs
        except Exception as e:
            print(e)



    #################################################################################
    #                                                                               #
    #       Functions below are application specified functions                     #
    #                                                                               #
    #       Use prefix: "get_" for single item lookup                               #
    #       Use prefix: "list_" for multiple items lookup                           #
    #                                                                               #
    #       By default, the result will be a DataFrame                              #
    #                                                                               #
    #################################################################################

    def get_symbol_rt_price(self, symbol):

        _res = self.getQuotes(symbol)

        _df = DataFrame(_res)
        print(_df)
        _df.set_index("StockSymbol", inplace=True)
        return _df


if __name__ == '__main__':

    test = GoogleUtil()
    # sdf = utility.get_popular_stocks()
    # print(test.get_YTD("AAPL"))
    df = test.get_historical("SPY", "2010-01-01", "2016-12-31")
    print(df)
    # df  = test.get_all_YTDs(sdf)