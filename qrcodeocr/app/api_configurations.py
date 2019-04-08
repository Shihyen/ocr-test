# -*- coding: utf8 -*-
import logging
import json
import datetime, time

from flask_restful import request, Resource
from qrcodeocr.util.mysqlutil import MySQLUtil
from qrcodeocr.mongoutil.funddetails import FundDetails
from qrcodeocr.util import utility

import pandas as pd
ts = int(str(time.time()).split('.')[0])
datestr = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')



def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        #print("know type: %s" % x)
        return x.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(x, datetime.date):
        #print("know type: %s" % x)
        return x.strftime('%Y-%m-%d')

    #print ("Unknown type: %s" % x)



class ApiConfigurations(Resource):
    def __init__(self):
        """
        initialize for utilities
        """

        self.mysqlutil = MySQLUtil()
        self.logger = logging.getLogger(__name__)
        #print(config_name)


    """
    api to retrieve currency rate
    """
    def get(self, config_name):
        try:
            conditions = request.args.get('conditions')
            wheres = " WHERE 1 = 1 "
            if conditions != None:
                params = json.loads(conditions)
                for item in params:
                    if isinstance(params[item], list):
                        wheres = wheres + " AND " + item + " IN ('"
                        wheres = wheres + "','".join(params[item]) + "')"
                    else:
                        wheres = wheres + " AND " + item + " = '"
                        wheres = wheres + params[item] + "'"
            # print(wheres)

            sql = ("SELECT * FROM %s  %s " % (config_name, wheres))
            res = self.mysqlutil.fetchall(sql)
            #print(res)
            data = json.dumps([dict(r) for r in res], default=datetime_handler)
            #print(data)
            return utility.json_return(200, data=json.loads(data))
        except Exception as e:
            return utility.json_return(400, message = str(e))

    def post(self, config_name):
        params = request.get_json(cache=False,silent=True)
        key = []
        value = []
        try:
            for item in params:
                # print(item)
                key.append(item)
                value.append(params[item])

            sql = "INSERT INTO " + config_name + "(`" + "`,`".join(key) + "`) VALUES(" + ",".join(['%s' for i in key]) + ")"
            res = self.mysqlutil.insert(sql, value)
            return utility.json_return(200, data = res)
        except Exception as e:
            return utility.json_return(400, message = str(e))

    def delete(self, config_name):
        params = request.get_json(cache=False,silent=True)
        key = []
        value = []
        if 'id' not in params:
            return utility.json_return(400, message = 'Params error')

        for item in params:
            key.append(item)
            value.append(params[item])
        try:
            sql = "DELETE FROM " + config_name + " WHERE id = %s "
            res = self.mysqlutil.update(sql, params['id'])
            return utility.json_return(200, data=res)

        except Exception as e:
            return utility.json_return(400, message = str(e))

    def put(self, config_name):
        params = request.get_json(cache=False,silent=True)
        key = []
        value = []
        if 'id' not in params:
            return utility.json_return(400, message = 'Params error')

        for item in params:
            key.append(item)
            value.append(params[item])
        try:
            ts = int(str(time.time()).split('.')[0])
            datestr = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            key.append('updated_at')
            value.append(datestr)
            value.append(params['id'])
            sql = "UPDATE " + config_name + " SET " + ", ".join( ('`' + k + '` = %s') for k in key ) + " WHERE id = %s "
            res = self.mysqlutil.update(sql, value)
            return utility.json_return(200, data=res)
        except Exception as e:
            return utility.json_return(400, message = str(e))



class ApiConfigurationsDumper(Resource):
    def __init__(self):
        """
        initialize for utilities
        """

        self.mysqlutil = MySQLUtil()
        self.logger = logging.getLogger(__name__)
        #print(config_name)


    def post(self, source_config, target_config):
        params = request.get_json(cache=False, silent=True)
        key = []
        value = []
        # try:
        conditions = []
        for item in params:
            print(item)
            if item == 'conditions':
                for condition in params[item]:
                    conditions.append(condition)
                continue
            key.append(item)
            value.append(params[item])

        if len(conditions) > 0:
            sql = "SELECT * FROM " + source_config + " WHERE " + ','.join(
                [str(a) + " = " + str(b) for a, b in zip(conditions, list(params['conditions'].values()))])
        else:
            sql = "SELECT * FROM " + source_config

        res = self.mysqlutil.fetchall(sql)
        data = json.dumps([dict(r) for r in res], default=datetime_handler)

        key.append('json')
        value.append(data)

        sql = "INSERT INTO " + target_config + "(" + ",".join(key) + ") VALUES(" + ",".join(['%s' for i in key]) + ")"

        res = self.mysqlutil.insert(sql, value)
        return utility.json_return(200, data = res)



#Fund Pool 的特殊規則
class ApiConfigurationsFundPool(Resource):
    def __init__(self):
        """
        initialize for utilities
        """

        self.mysqlutil = MySQLUtil()
        self.mongo_details = FundDetails()
        self.logger = logging.getLogger(__name__)
        #print(config_name)


    def get(self):
        sql = "SELECT DISTINCT pool_id, pool_name FROM	fund_pool WHERE	enabled = 1 ORDER BY pool_id DESC"
        res = self.mysqlutil.fetchall(sql)
        if res is None:
            return {}

        data = json.dumps([dict(r) for r in res], default=datetime_handler)

        return utility.json_return(200, data=json.loads(data))

    def post(self):
        #try:
            params = request.get_json(cache=False, silent=True)

            # fundid 轉換成 majorfundid
            major_fundid_dict, params['funds'] = self.get_major_fund_id(params['funds'])

            # 檢查是否有相同的pool_name
            duplicated, pool_id = self.check_pool_id(params['pool_name'])
            if duplicated:
                return utility.json_return(200, data={"result": 'duplicated', "pool_id": pool_id, "major_fundid": major_fundid_dict})


            # 建立fund_pool
            self.fundpool_creator(pool_id, params)

            return utility.json_return(200, data = {"result": 'success', "pool_id": pool_id, "major_fundid": major_fundid_dict})

    def put(self):
        #try:
            params = request.get_json(cache=False, silent=True)
            fund_list = "','".join([i for i in params['fund_list']])
            candidated_list = "','".join([i for i in params['candidated_list']])

            if len(fund_list) == 0:
                return utility.json_return(400, message='fund list required.')
            if len(candidated_list) < 0:
                return utility.json_return(400, message='candidated list required.')
            if 'pool_id' not in params:
                return utility.json_return(400, message='pool_id required.')

            sql = "UPDATE fund_pool SET enabled = 0, candidated = 0 WHERE pool_id = %s "
            self.mysqlutil.update(sql, (params['pool_id']))

            sql = ("UPDATE fund_pool SET enabled = 1 WHERE fund_id IN ('%s') AND pool_id = %s " % (fund_list, '%s'))
            f = self.mysqlutil.update(sql, (params['pool_id']))

            sql = ("UPDATE fund_pool SET candidated = 1 WHERE fund_id IN ('%s') AND pool_id = %s " % (candidated_list, '%s'))
            c = self.mysqlutil.update(sql, (params['pool_id']))
            res = f+c

            return utility.json_return(200, data = {"result": 'success', "data": res})

        #
        # except Exception as e:
        #     return self.json_return(400, message = str(e))
    def check_pool_id(self, pool_name):

        sql = "SELECT pool_id FROM fund_pool WHERE pool_name = %s LIMIT 1"

        # 重複的pool name(條件)不儲存，未來加入user_id
        res = self.mysqlutil.fetchone(sql, (pool_name))
        # print(res)
        if res is not None:
            sql = "UPDATE fund_pool SET enabled = 1 WHERE pool_id = %s "
            self.mysqlutil.update(sql, (res['pool_id']))
            return True, res['pool_id']

        sql = "SELECT pool_id FROM fund_pool ORDER BY id DESC LIMIT 1"
        res = self.mysqlutil.fetchone(sql)
        if res is None:
            pool_id = 1
        else:
            pool_id = res['pool_id'] + 1

        return False, pool_id

    def fundpool_creator(self, pool_id, params):
        key = ['start_date', 'end_date', 'pool_name', 'pool_id', 'fund_id', 'params']
        value = []

        for fund_id in params['funds']:
            value.append("('%s','%s','%s','%s','%s','%s')" % (
            params['start_date'], params['end_date'], params['pool_name'], pool_id, fund_id,
            json.dumps(params['params'])))

        sql = "INSERT INTO fund_pool (" + ",".join(key) + ") VALUES %s " % (",".join([i for i in value]))

        return  self.mysqlutil.insert(sql)

    def get_major_fund_id(self, fund_list):

        majorFundIdList = list(self.mongo_details.get_fundlist_details(fund_list))
        df = pd.DataFrame(majorFundIdList)

        result = {}
        records = (df[['majorHowfundId','howfundId']].to_dict(orient='records'))
        for item in records:
            if item['majorHowfundId'] not in result:
                result[item['majorHowfundId']] = list([])

            result[item['majorHowfundId']].append(item['howfundId'])

        return result, list(set(list(df['majorHowfundId'])))