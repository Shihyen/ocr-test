# -*- coding: utf-8 -*-

import codecs
import json


class IOUtil:
    def __init__(self):
        pass

    def get_fund_composition(self, fund_id):

        try:
            # with codecs.open('../data/get_fund_portfolio_howF2935.json', encoding='utf-8', mode='r') as data_file:
            #     data = json.load(data_file)
            #     print(data)

            input_file = file("../data/get_fund_portfolio_howF2935.json", "r")
            # need to use codecs for output to avoid error in json.dump
            output_file = codecs.open("/tmp/output_file.json", "w", encoding="utf-8")

            # read the file and decode possible UTF-8 signature at the beginning
            # which can be the case in some files.
            data = json.loads(input_file.read().decode("utf-8"))
            json.dump(data, output_file, indent=4, sort_keys=True, ensure_ascii=False)

        except:
            print("Unexpected error")

        return data

    def create_json(self):
        data = {}
        data['howF2935'] = 'howF2935'

        hold = {}
        hold['date'] = '20161201'

        hold_data_list = []

        hold_data_list.append(dict([("RLCONS 0PCT 290121 CV", 6.55514)]))

        hold_data_list.append(dict([("CRRC CORP LTD 0PCT 050221 CV", 6.30473)]))
        hold_data_list.append(dict([("CHINA OVERS FIN 0 050123 CV", 5.79021)]))
        hold['data'] = hold_data_list

        data['hold'] = hold
        print(data)
        print(json.dumps(data))
