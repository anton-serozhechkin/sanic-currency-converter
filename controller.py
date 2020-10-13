import os
import dotenv
from binance.client import Client
from sanic.response import json, html, text
from jinja2 import Environment, PackageLoader, select_autoescape
from decimal import Decimal
from binance.exceptions import BinanceAPIException
import hmac
import requests
import binascii
import hashlib

class Controller:


    def __init__(self, request, api_key, api_secret):
        self._request = request
        # init binance client 
        self.__client = Client(api_key, api_secret)
        self.__api_key = api_key
        # create dir for templates
        self._env = Environment(loader=PackageLoader('main', 'templates'), autoescape=select_autoescape(['html', 'xml', 'tpl']))

    
    def __calc(self, symbol_ticker, in_amount):
        # get price from args
        price = symbol_ticker['price']
        # calculate excange result
        calculate_result = Decimal(price) * Decimal(in_amount.strip("'"))
        return calculate_result


    def _responce(self):
        # main view
        # get status and data 
        status, data = self.__get_price()
        if status == 'OK':
            # return func that create tamplate, pass data into
            return self._get_template('index.html', title='Calc sanic',data=data)
        else:
            return self._get_template('index.html', title='Error', data=data)


    def _get_template(self, tpl, **kwargs):
        # get file .html with new from args
        template = self._env.get_template(tpl)
        # pass kwargs in template
        get_template = html(template.render(kwargs))
        return get_template


    def __generate_sign(self):
        # sort list by alphabet
        result = sorted(self.__strip_currency())
        # create part of sign
        # example: 2BTCUSDT
        prepare_sign = "{}{}{}".format(result[0], result[1], result[2])
        # encode strings 
        api_key_bytes = self.__api_key.encode('UTF-8')
        prepare_sign_bytes = prepare_sign.encode('UTF-8')
        # create signature using hmac lib with alg sha256
        signature = hmac.new(api_key_bytes, prepare_sign_bytes, hashlib.sha256).hexdigest()
        return signature


    def __check_sign(self):
        signature = self.__generate_sign()
        # check if sign in requests headers
        if 'sign' in self._request.headers:
            # check sign from request and real sign
            if self._request.headers['sign'] == signature:
                data = 'OK'
            else:
                data = 'Signature from header isnt valid'
        else:
            data = 'Not found signature in headers'
        return data, signature

    def __get_price(self):
        status = 'ERROR'
        # check if all nessesary params were pass 
        if "in_currency" not in self._request.args:
            data = {"status": status, "msg": "The currency you want to exchange is not specified"}
        elif "out_currency" not in self._request.args:
            data = {"status": status, "msg": "Output currency not specified"}
        elif "in_amount" not in self._request.args:
            data = {"status": status, "msg": "The amount of currency is not specified"}
        else:
            # get request of check sign
            check_sign, signature = self.__check_sign()
            if check_sign == "OK":
                result_strip_currency = self.__strip_currency()
                symbol = "{}{}".format(result_strip_currency[0], result_strip_currency[1])
                try:
                    status = "OK"
                    # get data rate from binance api
                    symbol_ticker = self.__client.get_symbol_ticker(params={'symbol': symbol})
                    data = {"rate": symbol_ticker, "out_amount": self.__calc(symbol_ticker, result_strip_currency[2])}
                # if symbols arent exist
                except BinanceAPIException:
                    status = 'ERROR'
                    data = {"status": status, "msg": "Make sure the names of the currencies you entered are correct"}
            else:
                data = {"status": status, "msg": check_sign, "Example!!! Paste it in headers(its valid signature)": signature}
        return status, data


    def __strip_currency(self):
        # format params from request
        strip_in_currency = str(self._request.args["in_currency"]).strip('[]"')
        strip_out_currency = str(self._request.args["out_currency"]).strip('[]"')
        in_amount = str(self._request.args["in_amount"]).strip('[]"')
        result = [strip_in_currency.strip("'"), strip_out_currency.strip("'"), in_amount.strip("'")]
        return result
