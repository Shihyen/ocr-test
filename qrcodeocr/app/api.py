# -*- coding: utf8 -*-
import logging
import time
import fnmatch, re
from qrcodeocr.common import api_config
from qrcodeocr.app.api_ocr import ApiOCR

from flask import Flask, g, request
from flask import jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from werkzeug.contrib.fixers import ProxyFix # gunicorn
# from flask_caching import Cache #Redis Cache
from werkzeug.contrib.cache import SimpleCache, RedisCache
import os


logger = logging.getLogger(__name__)

# cache = Cache(config=api_config.CACHE_CONFIG) #Redis Cache
cache = SimpleCache()

app = Flask(__name__)
# app.static_folder = 'static'
app._static_folder = os.path.abspath("static/")

# avoiding mysql server has gone away
# https://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600

# cache.init_app(app)

api = Api(app, catch_all_404s=True)

# cors = CORS(app, resources={r"/%s/*"%(api_config.API_PREX): {"origins": ["http://swagger-ui.howinvest.com","https://local.howinvest.com","https://how-fintech-smart-select.firebaseapp.com"]}})

class ApiHome(Resource):
    def get(self):
        logger.info("API HOME")
        return "Common Wealth API Home"


####################################################
## Set the Api resource routing here
####################################################

# root
api.add_resource(ApiHome, '/')

api.add_resource(ApiOCR, api_config.get_url_path('api_ocr'))

@app.before_request
def before_request():
    """
    Save time when the request started.

    :return: None
    """

    g.start = time.time()
    g.cached = False

    # # check cache
    # if not request.values:
    if (request.args.get('nocache') != '1') and (request.method not in ('POST','OPTIONS')):
        response = cache.get(request.full_path)
        if response:
            g.cached = True
            return response

    return None



# @app.after_request
# def after_request(response):
#     """
#     Write out a log entry for the request.

#     :return: Flask response
#     """

#     if 'start' in g:
#         response_time = (time.time() - g.start)
#     else:
#         response_time = 0

#     response_time_in_ms = int(response_time * 1000)

#     # if not request.values:
#     if (g.cached):
#         response_time_in_ms = 'CACHED'

#     # only cache successfully response
#     # elif (response.status_code == 200) and (request.method not in ('POST','OPTIONS')):
#     #     timeout = api_config.get_cache_timeout(request.url_rule.rule)
#     #     cacheKey = request.full_path.replace('nocache=1','')
#     #     cache.set(cacheKey, response, timeout=timeout)
#     #     logging.info("CACHE_SET key:[%s] is setting cache for [%i]seconds", cacheKey, timeout)

#     params = {
#         'method': request.method,
#         'in': response_time_in_ms,
#         'url': request.full_path,
#         'ip': request.remote_addr,
#         'status': response.status
#     }
#     logger.info('[APILOG] Time(ms):[%(in)s] Client:[%(ip)s] URL:[%(url)s] Status:[%(status)s]', params)

#     allow_origin_regex = ['how-fintech-smart-select.firebaseapp.com', '*.howinvest.com']

#     if 'HTTP_ORIGIN' in request.environ:
#         domain = re.sub(r"/|https:|http:", "", request.environ['HTTP_ORIGIN'])
#         for pattern in allow_origin_regex:
#             filtered = fnmatch.filter([domain], pattern)
#             if len(filtered) > 0:
#                 response.headers.add('Access-Control-Allow-Origin', request.environ['HTTP_ORIGIN'] )
#                 response.headers.add('Access-Control-Allow-Headers', 'access-control-allow-origin,content-type,x-xsrf-token')
#                 response.headers.add('Access-Control-Allow-Methods', 'GET,POST')

#     return response

# @app.errorhandler(Exception)
# def handle_invalid_usage(error):
#     print("========== ERROR ==========")
#     print(error)
#     # print(type(error))
#     # if type(error) == dict:
#     # response = jsonify(error.to_dict())
#     # response.status_code = error.status_code
#     # else:
#     #     response = {"code": 400, "status_code": None}


#     return error

def main():
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
    return 0

app.wsgi_app = ProxyFix(app.wsgi_app) # new

if __name__ == '__main__':
    exit(main())
