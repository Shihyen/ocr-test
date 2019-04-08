# -*- coding: utf-8 -*-
import argparse
import configparser
import logging.config
import os

# loading config
config = configparser.ConfigParser()
config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ini/config.ini'))
config.read(config_file)


"""configure.py: all configuration setting used in the algorithm"""

__author__ = "Raymond Lee"
__copyright__ = "Copyright 2017, Planet Earth"

# fund_list_csv = ['01TGBAMU', '02BGF', '03ABFCP', '04HHPA', '05FEHYAAE',
#                  '06BJSMOA', '07PEAEAU', '08IPEAAU', '09AFIEMDA']
#
# bond_funds = ['01TGBAMU', '03ABFCP', '05FEHYAAE', '09AFIEMDA']

fund_list_csv = ['howF1294', 'howF3946', 'howF180', 'howF1894', 'howF1620', 'howF4002', 'howF3112', 'howF2170',
                 'howF676']
bond_funds = ['howF1294', 'howF180', 'howF1620', 'howF676']

robot_pf_name_list = ['Safe0', 'Safe1', 'Safe2', 'General0', 'General1', 'General2', 'Aggressive0', 'Aggressive1',
                      'Aggressive2']

number_of_target_return = 100  # number of target expected return

'''
## Risky asset percentage of portfolio
stocks_percentage = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]  # risky assets percentage
percentage_list = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]  # used for checking
stock_percentage_risk_level_map = {'0.1': 'Criteria1',
                                   '0.2': 'Criteria2',
                                   '0.3': 'Criteria3',        # 0.3, weight [ 0.05 ~ 0.4 ] works
                                   '0.4': 'Criteria4',     # 0.4, weight [ 0.05 ~ 0.4 ] works
                                   '0.5': 'Criteria5',     # 0.5, weight [ 0.05 ~ 0.4 ] works
                                   '0.6': 'Criteria6',     # 0.6, weight [ 0.05 ~ 0.4 ] works
                                   '0.7': 'Criteria7',  # 0.7, weight [ 0.05 ~ 0.4 ] works
                                   '0.8': 'Criteria8',  # 0.8, weight [ 0.05 ~ 0.4 ] works
                                   }
'''

stocks_percentage = [0.1]  # risky assets percentage
percentage_list = [0.1]  # used for checking
stock_percentage_risk_level_map = {'0.1': 'Criteria1'}

initial_capital = 1000000  ## For calculating optimized portfolio
monthly_invest = 10000  ## For calculating projected value

rf = 0.01  ## Risk-free rate annual 1%
trans_fee = 0.005  ## Transaction fee 0.5%

# number of risk levels
risk_levels = 9

## bond position in the fund list
bond_list = [0, 2, 4, 8]

enable_upper_lower_bound = False

enable_stock_ratio = False
## upper bound of portfolio weight
upper_weight = 0.4

## lower bound of portfolio weight
lower_weight = 0.00

## Input data window start date
start_date = '2006-12-07'

## Input data window end date
end_date = '2016-12-05'

## back test window start date
bk_start_date = '2015-12-08'

## back test window end date
bk_end_date = '2016-12-05'

##
annualized_shift = 252

## Data date for backwarding for rolling window
last_data_date = '2016-12-07'

## RESTFUL API URL
api_fund_list = "http://howfintech.com/api/v1/fund/list/"
api_fund_detail = "http://howfintech.com/api/v1/fund/detail"
auth_token = '2c0a50b4a76d83d77cae1f859a40de55c0b07877'

# MySql related data
# db_host = 'localhost'
# db_user = 'howdev'
# db_pw   = 'howdev'
# db_name = 'hopp'

db_host = config['mysql']['host']
db_user = config['mysql']['user']
db_pw = config['mysql']['pwd']
db_name = config['mysql']['db']
db_portfolio_db = config['mysql']['portfolio_db']

db_logEnabled = True

t_op_pf = 'optimized_portfolio'
t_rk_pf = 'risk_preference'
t_rt_pb = 'return_probability'

mysql_url = 'mysql://' + config['mysql']['user'] + ':' + config['mysql']['pwd'] + '@' + config['mysql']['host'] + ':3306/' + config['mysql']['db'] + '?charset=utf8'

## Confidential interval value
CI = {'90': '1.65', '95': '1.96', '99': '2.58'}

## Projection scenarios
ProjScen = {'mean': '0', 'high': '1.0', 'low': '-1.0'}
# ProjScen = {'mean': '0'}


## mongo
MONGO_URI = config['mongo']['host']
DB = config['mongo']['db']
USERNAME = config['mongo']['user']
PASSWORD =  config['mongo']['pwd']

##
mongo_host = config['mongo']['host']
mongo_port = config['mongo']['port']
mongo_user = config['mongo']['user']
mongo_pw = config['mongo']['pwd']
mongo_db = config['mongo']['db']
mongo_auth_db = config['mongo'].get('auth', config['mongo']['db'])


# mongo_user = 'dev'
# mongo_pw = 'egraceshockedbyjim'
# mongo_db = 'sourceDev'
mongo_logEnabled = True

# pandas dataframe
dataframe_fillna_method = "ffill"

google_logEnabled = True
yahoo_logEnabled = True

elasticsearch_host = '192.168.10.208'
elasticsearch_port = 9200

api_algo_url = config['api']['algo_url']
api_algo_user = config['api']['algo_user']
api_algo_psw = config['api']['algo_psw']

redis_host = config['cache']['host']
env = config['env']['env']