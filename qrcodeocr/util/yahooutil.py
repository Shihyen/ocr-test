# -*- coding: utf-8 -*-
import json
import logging
import ssl
import time
import urllib
import urllib.parse
import urllib.request

from qrcodeocr.common import configure
from qrcodeocr.util import utility

# import yahoo_finance as yf
# import pprint

logger = logging.getLogger(__name__)
ssl._create_default_https_context = ssl._create_unverified_context


class YahooUtil:
    def __init__(self):
        self.logEnabled = configure.yahoo_logEnabled

    def log(self, st, symbol):
        if (self.logEnabled):
            timediff = int((time.time() - st) * 1000)
            logger.info(
                '[YahooFinance] Time(ms):[%s] Symbol(s):[%s]',
                timediff, symbol)

    def query_symbols(self, symbols):
        st = time.time()
        start_date = '2016-12-31'
        end_date = '2017-01-06'
        result = []
        try:
            columns = 'symbol, Name, LastTradeDate, LastTradeTime, LastTradePriceOnly, PreviousClose, Change, PercentChange, Volume'
            symbols_str = str(symbols).replace("[", "").replace("]", "")
            query_str = 'select %s from yahoo.finance.historicaldata where symbol in (%s) and startDate = "%s" and endDate = "%s"' % (columns, symbols_str, start_date, end_date)
            print(query_str)
            base_url = 'https://query.yahooapis.com/v1/public/yql?'
            query = {
                'q': query_str,
                'format': 'json',
                'env': 'store://datatables.org/alltableswithkeys'
            }

            url = base_url + urllib.parse.urlencode(query)
            data = urllib.request.urlopen(url).read().decode('utf-8')
            data_dic = json.loads(data)
            count = data_dic['query'].get("count")
            if (count <= 1):
                quote = data_dic['query']['results']['quote']
                _res = self.parse_quote(quote)
                result.append(_res)
            else:
                for quote in data_dic['query']['results']['quote']:
                    _res = self.parse_quote(quote)
                    result.append(_res)

        except Exception as e:
            logger.error("read_sql exception: " + str(e))
        self.log(st, symbols)
        return result

    def parse_quote(self, quote):
        _res = {}
        _res['symbol'] = quote.get("symbol")
        _res['name'] = quote.get("Name")
        _res['tradeDate'] = utility.format_date(quote.get("LastTradeDate"), '%m/%d/%Y')
        _res['local'] = utility.format_24time(quote.get("LastTradeTime"))
        _res['quote'] = quote.get("LastTradePriceOnly")
        _res['prevClose'] = quote.get("PreviousClose")
        _res['change'] = eval(quote.get("Change"))
        _res['changePercent'] = utility.convert_percent_to_float(quote.get("PercentChange"))
        _res['volume'] = quote.get("Volume")
        return _res

    def get_symbol_rt_quote(self, symbol_df):
        """
        Just compose yahoo finance uri to get specific stock infos
        """
        yahoo_base_url = 'https://query.yahooapis.com/v1/public/yql?q='
        yahoo_params = '&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys'
        stock_list = list(symbol_df['symbol_yahoo'])
        symbol_df.reset_index(inplace=True)
        symbol_df.set_index('symbol_yahoo', inplace=True)
        token_str = "env 'store://datatables.org/alltableswithkeys'; "
        query_str = token_str+'select * from yahoo.finance.quotes where symbol in (%s)'
        stock_str = ''
        for stock in stock_list:
            stock_str += '"' + stock + '",'
        query_str %= stock_str[:-1]
        query_str = urllib.parse.quote(query_str)
        request_url = yahoo_base_url + query_str + yahoo_params
        req = urllib.request.Request(request_url)
        reponse = urllib.request.urlopen(req).read()
        stock_infos = json.loads(reponse)['query']['results']['quote']
        for info in stock_infos:
            try:
                stock_name = info['symbol']
                symbol_df.set_value(
                    stock_name,
                    'tradeDate',
                    utility.format_date(info["LastTradeDate"], '%m/%d/%Y'))
                symbol_df.set_value(
                    stock_name,
                    'local',
                    utility.format_24time(info["LastTradeTime"]))
                symbol_df.set_value(
                    stock_name,
                    'quote',
                    float(info['LastTradePriceOnly']))
                symbol_df.set_value(
                    stock_name,
                    'prevClose',
                    info['PreviousClose'])
                symbol_df.set_value(
                    stock_name,
                    'change',
                    float(eval(info['Change'])))
                symbol_df.set_value(
                    stock_name,
                    'changePercent',
                    utility.convert_percent_to_float(info['PercentChange']))
                last_price = float(info['LastTradePriceOnly'])
                ytd = float(symbol_df.get_value(stock_name, 'ytd'))
                symbol_df.set_value(
                    stock_name,
                    'YTDROI',
                    utility.format_float((last_price - ytd) / ytd))
            except Exception as e:
                logger.error("yahoo exception: " + str(e))
        return symbol_df

    def list_symbol_rt_price(self, symbols):
        _res = self.query_symbols(symbols)
        return _res
