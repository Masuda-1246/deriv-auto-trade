# run it like PYTHONPATH=. python3 examples/simple_bot1.py
import sys
import asyncio
import os
from deriv_api import DerivAPI
import pprint
from dotenv import load_dotenv
load_dotenv()

app_id = 1089
api_token = os.getenv('DERIV_TOKEN', '')

if len(api_token) == 0:
    sys.exit("DERIV_TOKEN environment variable is not set")


async def sample_calls():
    api = DerivAPI(app_id=app_id)

    response = await api.ping({'ping': 1})
    if response['ping']:
        print(response['ping'])



    # Authorize
    await api.authorize(api_token)

    # Get Balance
    response = await api.balance()
    response = response['balance']
    currency = response['currency']
    print("Your current balance is", response['currency'], response['balance'])
    # profit table
    profit_table = await api.profit_table({"profit_table": 1, "description": 1, "sort": "DESC", "limit": 10})
    pprint.pprint(profit_table)
    limit = 100
    rofit_table = await api.profit_table({"profit_table": 1, "description": 1, "sort": "DESC", "limit": limit})
    win_count = 0
    for item in rofit_table['profit_table']['transactions']:
        if item['sell_price'] != 0:
            win_count = win_count + 1
    rate = win_count / limit
    print(rate)

    await api.clear()


asyncio.run(sample_calls())