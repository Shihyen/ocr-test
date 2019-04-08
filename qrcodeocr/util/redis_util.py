# -*- coding: utf-8 -*-
import logging

from flask import request
from werkzeug.contrib.cache import SimpleCache

CACHE_TIMEOUT = 180

cache = SimpleCache()
logger = logging.getLogger(__name__)


class cached(object):
    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            cacheKey = self.get_cachekey(f, args, kwargs)
            data = cache.get(cacheKey)
            if data is None:
                data = f(*args, **kwargs)
                cache.set(cacheKey, data, self.timeout)
                logger.info('[CACHE_SET] cacheKey:[%s] timeout:[%i]', cacheKey, self.timeout)
            else:
                logger.info('[CACHE_HIT] cacheKey:[%s]', cacheKey)
            return data

        return decorator

    def get_cachekey(self, f, args, kwargs):
        cacheKey = "%s|%s|%s" % (str(f.__name__), str(args[1:]), str(kwargs))
        return cacheKey
