import csv
import pprint
from app.models.base import Tick

ticks = Tick.get_all_ticks(20000)

with open('./sample_writer_row.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "price"])
    for tick in ticks:
        writer.writerow([tick.timestamp, tick.price])
