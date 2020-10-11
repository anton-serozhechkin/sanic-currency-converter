import os
import dotenv
from binance.client import Client
from sanic.response import json, html, text
from jinja2 import Environment, PackageLoader, select_autoescape
from decimal import Decimal
from binance.exceptions import BinanceAPIException
import hmac

class Controller:


    def __init__(self, request, request_args, api_key, api_secret):
        self._request = request
        self._request_args = request_args
        self.__client = Client(api_key, api_secret)
        self._env = Environment(loader=PackageLoader('main', 'templates'), autoescape=select_autoescape(['html', 'xml', 'tpl']))

    
    def __calc(self, symbol_ticker, in_amount):
        price = symbol_ticker['price']
        int_in_amount = in_amount.strip("'")
        calculate_result = Decimal(price) * Decimal(int_in_amount)
        return calculate_result


    def _responce(self):
        #if self._request == "POST":
        status, data = self.__get_price()
        if status == 'OK':
            return self._get_template('index.html', title='Request post',data=data)
        else:
            return self._get_template('index.html', title='Error', data=data)
        #else:
        #    return self._get_template('index.html', title='Request get')


    def _get_template(self, tpl, **kwargs):
        template = self._env.get_template(tpl)
        get_template = html(template.render(kwargs))
        return get_template


    def __get_price(self):
        print(self.__generate_sign())
        status = 'ERROR'
        if "in_currency" not in self._request_args:
            data = {"status": status, "msg": "The currency you want to exchange is not specified"}
        elif "out_currency" not in self._request_args:
            data = {"status": status, "msg": "Output currency not specified"}
        elif "in_amount" not in self._request_args:
            data = {"status": status, "msg": "The amount of currency is not specified"}
        else:
            result_strip_currency = self.__strip_currency()
            symbol = "{}{}".format(result_strip_currency[0], result_strip_currency[1])
            try:
                status = "OK"
                symbol_ticker = self.__client.get_symbol_ticker(params={'symbol': symbol})
                data = {"rate": symbol_ticker, "out_amount": self.__calc(symbol_ticker, result_strip_currency[2])}
            except BinanceAPIException:
                status = 'ERROR'
                data = {"status": status, "msg": "Make sure the names of the currencies you entered are correct"}
        return status, data


    def __strip_currency(self):
        strip_in_currency = str(self._request_args["in_currency"]).strip('[]"')
        strip_out_currency = str(self._request_args["out_currency"]).strip('[]"')
        in_amount = str(self._request_args["in_amount"]).strip('[]"')
        result = [strip_in_currency.strip("'"), strip_out_currency.strip("'"), in_amount.strip("'")]
        return result

    
    def __generate_sign(self):
        result = sorted(self.__strip_currency())
        sign = "{}{}{}".format(result[0], result[1], result[2])
        return sign

    #def __check_sign(self):
