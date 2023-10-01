import configparser

config = configparser.ConfigParser()
config.read('settings.ini')

product_code=config['oanda']['product_code']

db_name = config['db']['name']
db_driver = config['db']['driver']

port = int(config['web']['port'])

trade_duration = config['pytrading']['trade_duration'].lower()
backtest = config['pytrading']['backtest']
use_percent = float(config['pytrading']['use_percent'])
past_period = int(config['pytrading']['past_period'])
stop_limit_percent = float(config['pytrading']['stop_limit_percent'])
num_ranking = int(config['pytrading']['num_ranking'])