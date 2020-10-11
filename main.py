from sanic import Sanic
from sanic.response import json, html, text
import dotenv
import os
from jinja2 import Environment, PackageLoader, select_autoescape
from controller import Controller
from binance.client import Client


dotenv_file = os.path.join(os.environ['PWD'], ".env")
load_file = dotenv.load_dotenv(dotenv_file)

api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']

app = Sanic("calc_sanic")


@app.route("/calc")#, methods=["POST"])
async def test(request):
  controller = Controller(request, request.args, api_key, api_secret)
  responce = controller._responce()
  return responce

app.run(host="0.0.0.0", port=8001)