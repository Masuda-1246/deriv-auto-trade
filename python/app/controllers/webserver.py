from flask import Flask, render_template, jsonify, request


import settings
from app.models.base import DataFrameCandle

app = Flask(__name__, template_folder="../views")

@app.route('/')
def index():
  app.logger.info("index")
  # for tick in all_ticks:
  #     print(f"time: {tick.timestamp}, price: {tick.price}")
  return render_template('./google.html')

@app.route('/api/ticks/', methods=['GET'])
def get_ticks():
  app.logger.info("get_ticks")
  df = DataFrameCandle()
  df.set_all_ticks()
  return jsonify(ticks=df.value), 200
def start():
  app.run(host="0.0.0.0", port=settings.port, threaded=True)