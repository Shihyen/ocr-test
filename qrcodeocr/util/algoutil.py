# -*- coding: utf-8 -*-
import json
import logging
import urllib
import urllib.parse
import urllib.request

import pandas as pd
from qrcodeocr.common import configure
from qrcodeocr.common import api_config
from qrcodeocr.util import utility


logger = logging.getLogger(__name__)


class AlgoUtil:

    def __init__(self):

        self.optimizedweight_url = ("%s/optimizedweight?date=%s&risklevel=%s" % (configure.api_algo_url, '%s', '%s'))
        # create a password manager
        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, configure.api_algo_url, 'howdev', 'how1234')
        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

    def send_request(self, url):

        try:
            res = urllib.request.urlopen(url).read().decode('utf-8')

            return res

        except Exception as e:
            logger.error("google gQ read_sql exception: %s %s " % (str(e), url))

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

    def get_robo_portfolio(self, date, risklevel):

        data = self.get_optimized_weight(date, risklevel)

        for k, v in data['weights'].items():
            data['weights'][k] = data['weights'].get(k).get('weight')

        return data


    def get_optimized_weight(self, date, risklevel):

        date = self.format_date(date)

        # add auto_fill parameter, default value from mysql api config
        mysql_config = api_config.get_mysql_config()

        url = (self.optimizedweight_url + "&autofill=%s") % (date, risklevel, mysql_config['default_arg_autofill'])
        logger.info(url)
        res = self.send_request(url)
        if res == None:
            return {}

        # result data as dictionary
        data = json.loads(res)

        data['date'] = utility.format_date_api(data['date'], from_format='%Y%m%d', to_format='%Y-%m-%d')
        data['risk_level'] = data.pop('risklevel')


        return data

    def get_rtn_std(self, date, risklevel):

        date = self.format_date(date)

        url = self.optimizedweight_url % (date, risklevel)
        #print(url)
        res = self.send_request(url)

        print(res)
        # result data as dictionary
        data = json.loads(res)

        rtn = data.get('return')
        std = data.get('std')

        return rtn, std

    def get_weightdf_by_risklevl(self, date, risklevel):

        date = self.format_date(date)

        url = self.optimizedweight_url % (date, risklevel)
        logger.info(url)
        res = self.send_request(url)
        logger.info(res)
        # result data as dictionary
        data = json.loads(res)
        logger.info(data)
        weights = data.get('weights')

        fund_list = []
        weight_list = []
        for k, v in weights.items():
            fund_list.append(k)
            weight_list.append(float(v.get('weight')))
        weights_df = pd.DataFrame(weight_list, index=fund_list, columns=['weight'])

        return weights_df


    def get_fund_candidate(self, date, risk_level, pool_id):


        date = self.format_date(date)

        url = ("%s/fundcandidates?date=%s&risklevel=%s&pool_id=%s&autofill=false&full=false&nocache=1" % (configure.api_algo_url, date, risk_level, pool_id))


        logger.info(url)
        res = self.send_request(url)
        if res == None:
            return {}

        # result data as dictionary
        data = json.loads(res)

        # data['date'] = utility.format_date_api(data['date'], from_format='%Y%m%d', to_format='%Y-%m-%d')
        # data['risk_level'] = data.pop('risklevel')


        return data


    def get_rebalance(self, date, risk_level, portfolio_id):

        url = ("%s/rebalancing?date=%s&risklevel=%s&portfolio_id=%s&autofill=false&full=false&nocache=1" % (configure.api_algo_url, date, risk_level, portfolio_id))

        logger.info(url)
        res = self.send_request(url)
        if res == None:
            return {}

        # result data as dictionary
        data = json.loads(res)

        # data['date'] = utility.format_date_api(data['date'], from_format='%Y%m%d', to_format='%Y-%m-%d')
        # data['risk_level'] = data.pop('risklevel')


        return data


    def get_portfolio_score(self, date, risk_level, portfolio_id):

        url = ("%s/portscore?date=%s&risklevel=%s&portfolio_id=%s&nocache=1" % (configure.api_algo_url, date, risk_level, portfolio_id))

        logger.info(url)
        res = self.send_request(url)
        if res == None:
            return {}

        # result data as dictionary
        data = json.loads(res)

        # data['date'] = utility.format_date_api(data['date'], from_format='%Y%m%d', to_format='%Y-%m-%d')
        # data['risk_level'] = data.pop('risklevel')


        return data


    def get_funds_healthy_check(self, date, risk_level, userfund):

        url = ("%s/optimizedweight?date=%s&risklevel=%s&userfund=%s&nocache=1" % (configure.api_algo_url, date, risk_level, userfund))

        logger.info(url)
        res = self.send_request(url)
        if res == None:
            return {}

        # result data as dictionary
        data = json.loads(res)

        # data['date'] = utility.format_date_api(data['date'], from_format='%Y%m%d', to_format='%Y-%m-%d')
        # data['risk_level'] = data.pop('risklevel')


        return data



    def format_date(self, date):
        if type(date) == str:
            return date.replace('-', '')
        else:
            return date


if __name__ == '__main__':
    test = AlgoUtil()
    data = test.get_robo_portfolio('20171001', '5')
    print(data)

    rtn, std = test.get_rtn_std('20170101', 3)
    print(rtn, std)

    res = test.get_weightdf_by_risklevl('20170101', 3)
    print(res)
