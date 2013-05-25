import time
from decimal import Decimal
import logging
import logging.config

import exchanges.campbx as exchange
import wallets.bitcoind as wallet
import config
import ledger
import utils

def setup_logging():
  """
  Based on http://docs.python.org/howto/logging.html#configuring-logging
  """
  dictLogConfig = {
    "version":1,
    "handlers":{
      "fileHandler":{
        "class":"logging.FileHandler",
        "formatter":"simpleFormatter",
        "filename":"localbitcoins.log"
        },
      "consoleHandler":{
        "class":"logging.StreamHandler",
        "formatter":"simpleFormatter",
        "stream":"ext://sys.stdout"
        }
      },        
    "loggers":{
      "localbitcoins":{
        "handlers":["fileHandler","consoleHandler"],
        "level":"INFO",
        }
      },
    "formatters":{
      "simpleFormatter":{
        "format":"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      }
    }
  }
 
  logging.config.dictConfig(dictLogConfig)
 
  logger = logging.getLogger("localbitcoins")
  logger.info("program started")
  return logger

def main():
  # setup
  setup_logging()

  send()

def send():
  # send user btc
  # prompt user for btc address to send coins to
  user_addr = utils.prompt_for_addr(lambda s: wallet.send_btc(s, Decimal('0.01')))

def buy():
  # echo current usd balance
  print "current usd balance: %s" % exchange.usd_balance()

  # echo ticker
  print "ticker: %s" % exchange.ticker()

  # prompt user for how many usd to exchange
  usd_to_receive = Decimal(utils.prompt("how much usd do you want to exchange?", "[0-9]+"))

  # subtract fee
  usd_to_exchange = usd_to_receive * (Decimal('1') / (Decimal('1') + config.commission))

  btc_to_send, coin_cost = exchange.market_buy(usd_to_exchange)

  # log exchange
  print "market cost to buy coins: %s" % coin_cost
  print "revenue to sell coins: %s" % usd_to_receive
  print "profit not including account deposit fees: %s" % (usd_to_receive - coin_cost)
  ledger.log(usd_to_receive, btc_to_send, coin_cost)

  # send user btc
  # prompt user for btc address to send coins to
  user_addr = utils.prompt_for_addr(lambda s: exchange.send_btc(btc_to_send, s))

if __name__ == "__main__":
  main()
