import time
from decimal import Decimal
import decimal
decimal.getcontext().prec = 2
import logging
logger = logging.getLogger('localbitcoins')

from campbx import CampBX

import book
import config

c = CampBX(config.username, config.password)

def usd_balance():
  return (u'Liquid USD' in c.my_funds() or None) and Decimal(c.my_funds()[u'Liquid USD'])

def ticker():
  return c.xticker()

def market_buy(usd):
  old_balance = usd_balance()

  fee = Decimal('1') - (Decimal('1') / (Decimal('1') + config.account_deposit_fee + config.market_order_fee))
  usd_to_exchange = Decimal(usd) * (Decimal('1') - fee)
  # keep track of how many bitcoins the user will receive
  btc_to_send = Decimal('0')

  bidasks = book.Book.parse(c.xdepth())
  bidasks.sort()

  order_ids = []

  while usd_to_exchange > 0:

    try:
      ask = bidasks.asks.pop(0)
    except IndexError:
      bidasks = book.Book.parse(c.xdepth())
      bidasks.sort()
      continue

    logger.info("there are %s bitcoins available at %s/btc" % (ask.size, ask.price))
    
    if ask.price * ask.size <= usd_to_exchange:
      logger.info("buying all of the lowest order")
      print ask.price, ask.size
      order = book.Order(ask.size, ask.price)
    else:
      logger.info("buying some of the lowest order")
      print ask.size, ask.price
      order = book.Order(Decimal(usd_to_exchange / ask.price), ask.price)
      print order

    if order.size < 0.01:
      break
    logger.info("buying %s bitcoins at %s/btc" % (order.size, order.price))

    try:
      resp = c.trade_enter({
        'TradeMode': 'QuickBuy',
        'Quantity': str(order.size),
        'Price': str(order.price)
      })
      print resp

    except HTTPError as e:
      logger.error("error: %s" % e.message)
      logger.info("negligible usd left: %s" % usd_to_exchange)
      logger.info("btc to receive: %s" % btc_to_send)
      time.sleep(1)
      continue

    
    usd_to_exchange -= order.size * order.price
    btc_to_send += order.size
    bidasks.subtract(book.Book(bids=[order], asks=[]))

  logger.info("negligible usd left: %s" % usd_to_exchange)
  logger.info("btc to receive: %s" % btc_to_send)

  # check to make sure all orders are filled
  # >>> c.my_orders()[u'Buy']
  # [{u'Info': u'No open Sell Orders'}]
  while True:
    my_buys = c.my_orders()[u'Buy']
    if len(my_buys) == 1 and u'Info' in my_buys[0] and my_buys[0][u'Info'] == u'No open Buy Orders':
      break
    else:
      logger.info("current buy orders: %s" % my_buys)
      time.sleep(1)
      continue

  # get coin cost
  new_balance = usd_balance()
  coin_cost = old_balance - new_balance

  return btc_to_send, coin_cost

def send_btc(to_addr, amount):
  # send amount of btc from campbx to addr
  c.send_btc({
    'BCTTo': to_addr, 
    'BCTAmt': str(amount)
  })
  logger.info("sent %s btc from campbx to %s" % (amount, to_addr))
