# -*- coding: utf8 -*-
import logging

from qrcodeocr.app.api_error import InvalidUsage
from flask_restful import Resource

logger = logging.getLogger(__name__)


class ApiBase(Resource):

    def __init__(self):
        """
        initialize for utilities
        """
        self.logger = logging.getLogger(__name__)

    def validate(**kwargs):


    def log(self, message):
        pass
