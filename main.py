from sanic import Sanic
from sanic.response import json, html, text
import dotenv
import os
from controller import Controller
from binance.client import Client

# checl if file exist
dotenv_file = os.path.join(os.environ['PWD'], ".env")
# load file from env
load_file = dotenv.load_dotenv(dotenv_file)

# get binance keys from env
api_key = os.environ['API_KEY']
api_secret = os.environ['API_SECRET']

# create new app
app = Sanic("calc_sanic")

# handle only POST requests
@app.route("/calc", methods=["POST"])
async def test(request):
  # create new instance and pass args
  controller = Controller(request, api_key, api_secret)
  # get responce
  responce = controller._responce()
  return responce

app.run(host="0.0.0.0", port=8002)
