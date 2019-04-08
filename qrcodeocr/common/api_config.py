# -*- coding: utf8 -*-

import logging
import os
import configparser
from qrcodeocr.util import utility



# loading config
config = configparser.ConfigParser()
config_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../ini/config.ini'))
config.read(config_file)
API_VERSION = 'v1'

if "API_PREFIX" in os.environ:
    API_PREX = os.environ['API_PREFIX']
else:
    API_PREX = config['env']['api_prefix']

if "SEARCH_FUND" in os.environ:
    API_SEARCH_FUND = os.environ['SEARCH_FUND']
else:
    API_SEARCH_FUND = config['env']['search_fund']

if "API_CANDIDATED" in os.environ:
    API_CANDIDATED = os.environ['API_CANDIDATED']
else:
    API_CANDIDATED = config['env']['candidated']

if "FUND_CODE" in os.environ:
    FUND_CODE = os.environ['FUND_CODE']
else:
    FUND_CODE = config['env']['fund_code']


# CACHE
CACHE_TYPE = 'redis' # simple for local file, redis for redis
CACHE_TIMEOUT = 30  # 30 seconds
CACHE_CONFIG = {
    'CACHE_TYPE': config['cache']['type'],
    'CACHE_REDIS_HOST': config['cache']['host'],
    'CACHE_REDIS_PORT': config['cache']['port'],
    'CACHE_REDIS_DB': config['cache']['db'],
    'CACHE_REDIS_PASSWORD': config['cache']['pwd'],
    'CACHE_KEY_PREFIX': config['cache']['prefix']
}

# api_indexprice
# cache_timeouts = utility.list_cache_timeouts()
logger = logging.getLogger(__name__)


def get_url_path(rule):
    """
    create the url path from prex and version
    :param rule:
    :return:
    """
    rule_url = "/%s/%s/%s" % (API_PREX, API_VERSION, rule)

    return rule_url


def get_cache_timeout(url_rule):
    """
    get the cache timeout value from the rule
    :param url_rule:
    :return:
    """
    timeout = CACHE_TIMEOUT
    # if url_rule in cache_timeouts:
    #     timeout = cache_timeouts.get(url_rule).get('timeout')

    return timeout

def get_mysql_config():
    mysql_config = {}

    mysqlutil = MySQLUtil()
    sql = ("SELECT * FROM algo_configuration WHERE type = 'api' ")
    res = mysqlutil.fetchall(sql)
    for item in res:
        mysql_config[item['name']] = item['value']

    return mysql_config