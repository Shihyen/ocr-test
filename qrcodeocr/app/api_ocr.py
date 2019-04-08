# -*- coding: utf8 -*-

# Smart Select 主程式庫，包含 smart_select, smart_select_category
# @version v1.0

import datetime
import json
import math
import logging
# from flask_restful import request
from flask_restful import Resource
import requests
# import urllib.request
import numpy as np
import cv2
import urllib
from urllib.parse import urlparse
from flask import Flask, request
from qrcodeocr.common import api_config

import uuid
import hashlib

def get_image(photo_url):
    resp = urllib.request.urlopen(photo_url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    return image

def azimuthAngle( x1,  y1,  x2,  y2):
    angle = 0.0
    dx = x2 - x1
    dy = y2 - y1
    print(dx)
    print(dy)
    if  x2 == x1:
        angle = math.pi / 2.0
        if  y2 == y1 :
            angle = 0.0
        elif y2 < y1 :
            angle = 3.0 * math.pi / 2.0
    elif x2 > x1 and y2 > y1:
        angle = math.atan(dx / dy)
    elif  x2 > x1 and  y2 < y1 :
        print("x2 > x1 and  y2 < y1")
        angle = math.atan(dy / dx)
    elif  x2 < x1 and y2 < y1 :
        print("uuuuuuuuuuuuuuuuuuuuuuu")
        # angle = math.pi + math.atan(dx / dy)
        angle = math.atan(dx / dy)
    elif  x2 < x1 and y2 > y1 :
        angle = 3.0 * math.pi / 2.0 + math.atan(dy / -dx)
    return (angle * 180 / math.pi)

# 逆时针旋转图像degree角度（原尺寸）
def rotateImage(src, degree):
    # 旋转中心为图像中心
    h, w = src.shape[:2]
    # 计算二维旋转的仿射变换矩阵
    RotateMatrix = cv2.getRotationMatrix2D((w/2.0, h/2.0), degree, 1)
    # print(RotateMatrix)
    # 仿射变换，背景色填充为白色
    rotate = cv2.warpAffine(src, RotateMatrix, (w, h), borderValue=(255, 255, 255))
    return rotate


class ApiOCR(Resource):
    """
        """
    def __init__(self):
        pass

    def get(self):
        try:

            result = None
            code = 200
            message = ""
            status = None

            photo_url = request.args.get('photo_url')
            filename = urlparse(photo_url)
            filepath = filename.path.split("/")

            image = get_image(photo_url)
            canvas = image
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            boxs = detect(image)
            print(boxs)

            left = boxs[1][1].tolist()
            right = boxs[1][2].tolist()

            

            degree = azimuthAngle(left[0], left[1], right[0], right[1])
            degree = degree + 90
            print("调整角度：", degree)

            canvas = image

            rotate = rotateImage(canvas, degree)

            rotate_file = "static/rotated_{}".format(filepath[-1])

            cv2.imwrite(rotate_file, rotate)
            
            rotate = cv2.imread(rotate_file)
            boxs = detect(rotate)

            left = boxs[2][1].tolist()
            right = boxs[2][3].tolist()

            x = left[0]
            y = left[1]
            w = right[0] - left[0]
            h = right[1] - left[1]
            # cv2.drawContours(rotate, boxs, -1,(0,0,255),3)

            crop_img = rotate[y:y+h, x:x+w]
            filename = "static/croped_{}".format(filepath[-1])
            cv2.imwrite(filename, crop_img)
            result = filename
            result = "%s%s" % (request.url_root, filename)
            # if sharing_data:
            #     result = json.loads(sharing_data)
            # else:
            #     message = "ERROR_SHARING_CODE"
            #     raise ValueError('ERROR_SHARING_CODE')

        except ValueError as e:
            template = "{0}"
            message = e.args[0]
            logger.debug(message)
            code = 400
            status = '400 Bad Request'

        except KeyError as e:
            template = "{0} exception occurred. Arguments: {1!r}"
            message = template.format(type(e).__name__, e.args)
            logger.debug(message)
            code = 400
            status = '400 Bad Request'

        except Exception as e:
            template = "{0} exception occurred. Arguments: {1!r}"
            message = template.format(type(e).__name__, e.args)
            logger.debug(message)
            code = 500
            status = '500 Internal Server Error'
        finally:
            return json_return(code, message, result), status




    def post(self):
        """

        依據條件查詢結果

        :rtype: dict
        """
        try:

            result = {}
            code = 200
            message = ""
            status = None

            params = request.get_json(cache=False, silent=True)

            sharing_code = self.hash_sharing_code(params)

            result = mysqlutil.save_smart_select_sharing(sharing_code, params)

            result = sharing_code

            # print(result)

        except Exception as e:
            template = "{0} exception occurred. Arguments: {1!r}"
            message = template.format(type(e).__name__, e.args)
            logger.debug(message)
            code = 500
            status = '500 Internal Server Error'
        finally:
            return json_return(code, message, result), status

    # @cache_util.cached(timeout=60*60*24)
    def hash_sharing_code(self, data):

        allow_index = ['']
        salt = uuid.uuid4().hex
        encode_data = urllib.parse.urlencode(data)
        return hashlib.sha256(salt.encode() + encode_data.encode()).hexdigest()


def json_return(code, message = '', data ={}):
    """

    將資料轉換成dict作為API回傳的統一格式

    :param code:
    :param message:
    :param data:
    :return:
    """
    return {'data': data, 'msg':message, 'code': code}


def json_fix(series):
    """

    將存在mysql的json欄位轉換，以免輸出成JSON的時候出錯。（for dataframe)

    :param series:
    :return: series
    """
    return json.loads(json.dumps(series, default=datetime_handler))





def detect(image):
    
    
    # convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # compute the Scharr gradient magnitude representation of the images
    # in both the x and y direction
    gradX = cv2.Sobel(gray, ddepth = cv2.CV_32F, dx = 1, dy = 0, ksize = -1)
    gradY = cv2.Sobel(gray, ddepth = cv2.CV_32F, dx = 0, dy = 1, ksize = -1)
    # cv2.imshow("test", gray)

    # subtract the y-gradient from the x-gradient
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)
    # cv2.imshow("test", gradient)

    # blur and threshold the image
    blurred = cv2.blur(gradient, (9, 9))
    (_, thresh) = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)
    # cv2.imshow("test", blurred)




    # construct a closing kernel and apply it to the thresholded image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # cv2.imshow("test", closed)

    # perform a series of erosions and dilations
    closed = cv2.erode(closed, None, iterations = 4)
    closed = cv2.dilate(closed, None, iterations = 4)
 
    # find the contours in the thresholded image
    (cnts, _) = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
 
    # if no contours were found, return None
    if len(cnts) == 0:
        return None

    # otherwise, sort the contours by area and compute the rotated
    # bounding box of the largest contour
    c = sorted(cnts, key = cv2.contourArea, reverse = True)
    if len(c) < 2:
        return None

    res = []
    for ci in range(0, 3):
        rect = cv2.minAreaRect(c[ci])
        box = np.int0(cv2.boxPoints(rect))
        res.append(box)
    # return the bounding box of the barcode
    return res