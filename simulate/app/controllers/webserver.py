from flask import Flask, render_template, jsonify, request
import sys
import os
from deriv_api import DerivAPI
from datetime import datetime

import settings
from app.models.base import Tick, Rating
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, template_folder="../views")

app_id = 1089
api_token = os.getenv('DERIV_TOKEN', '')

if len(api_token) == 0:
    sys.exit("DERIV_TOKEN environment variable is not set")


@app.route('/')
def index():
  app.logger.info("index")
  # for tick in all_ticks:
  #     print(f"time: {tick.timestamp}, price: {tick.price}")
  return render_template('./google.html')



@app.route('/api/get/profit_table', methods=['GET'])
async def get_profit_table():
  api = DerivAPI(app_id=app_id)
  app.logger.info("get_profit_table")
  await api.authorize(api_token)
  limit = 10
  rofit_table = await api.profit_table({"profit_table": 1, "description": 1, "sort": "DESC", "limit": limit})
  return jsonify(profit_table=rofit_table), 200

@app.route('/api/get/rate', methods=['GET'])
async def get_rate():
  api = DerivAPI(app_id=app_id)
  app.logger.info("get_wininngrate")
  await api.authorize(api_token)
  limit = 100
  rofit_table = await api.profit_table({"profit_table": 1, "description": 1, "sort": "DESC", "limit": limit})
  win_count = 0
  touch_count = 0
  touch_win_count = 0
  notouch_count = 0
  notouch_win_count = 0
  for item in rofit_table['profit_table']['transactions']:
      if item['payout'] > item['buy_price']*2: # notouch
          notouch_count = notouch_count + 1
          if item['sell_price'] != 0:
              win_count = win_count + 1
              notouch_win_count = notouch_win_count + 1
      else:
          touch_count = touch_count + 1
          if item['sell_price'] != 0:
              win_count = win_count + 1
              touch_win_count = touch_win_count + 1
  rate = win_count / limit
  touch_rate = touch_win_count / touch_count
  notouch_rate = 0 if notouch_count == 0 else notouch_win_count / notouch_count
  data = {
      'rate': rate,
      'touch_rate': touch_rate,
      'notouch_rate': notouch_rate,
      'limit': limit,
      'touch_count': touch_count,
      'notouch_count': notouch_count,
  }
  Rating.create(
      timestamp=datetime.now(),
      limit=limit,
      total_rating=rate,
      touch_limit=touch_count,
      touch_rating=touch_rate,
      notouch_limit=notouch_count,
      notouch_rating=notouch_rate
  )
  return jsonify(data=data), 200

def start():
  app.run(host="0.0.0.0", port=settings.port, threaded=True)