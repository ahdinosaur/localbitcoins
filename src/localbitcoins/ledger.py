# TODO use ledger instead of csv

import os
import os.path
import datetime
import csv

ledger_filename = os.path.join(os.path.dirname(__file__), "../../ledger.csv")
try:
  with open(ledger_filename): pass
except IOError:
  with open(ledger_filename, 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'usd_received', 'btc_sent', 'coin_cost'])

def log(usd_received, btc_sent, coin_cost):
  date = datetime.date.today().isoformat()
  with open(ledger_filename, 'a') as f:
    writer = csv.writer(f)
    writer.writerow([date, usd_received, btc_sent, coin_cost])


