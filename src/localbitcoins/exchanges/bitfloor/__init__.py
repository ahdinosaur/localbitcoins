import time
from decimal import Decimal
import logging

from requests.exceptions import HTTPError

import lib
import book
import config

bitfloor = lib.RAPI(product_id=1, key=config.key, secret=config.secret)

def market_buy(usd):
  fee = Decimal('1') - (Decimal('1') / (Decimal('1') + config.account_deposit_fee + config.market_order_fee))
  usd_to_exchange = Decimal(usd) * (Decimal('1') - fee)
  # keep track of how many bitcoins the user will receive
  btc_to_send = Decimal('0')

  bidasks = book.Book.parse(bitfloor.book(level=2))
  bidasks.sort()

  order_ids = []

  while usd_to_exchange > 0:

    try:
      ask = bidasks.asks.pop(0)
    except IndexError:
      bidasks = book.Book.parse(bitfloor.book(level=2))
      bidasks.sort()
      continue

    logging.info("there are %s bitcoins available at %s/btc" % (ask.size, ask.price))
    
    if ask.price * ask.size <= usd_to_exchange:
      order = book.Order(ask.size, bitfloor.floor_inc(ask.price))
    else:
      order = book.Order(bitfloor.floor_inc(usd_to_exchange / ask.price), bitfloor.floor_inc(ask.price))

    if order.size < 0.00001:
      break
    logging.info("buying %s bitcoins at %s/btc" % (order.size, order.price))

    try:
      resp = bitfloor.buy(size=order.size, price=order.price)
    except HTTPError as e:
      logging.error("error: %s" % e.message)
      logging.info("negligible usd left: %s" % usd_to_exchange)
      logging.info("btc to receive: %s" % btc_to_send)
      time.sleep(1)
      continue

    order_id = resp[u'order_id']
    order_ids.append(order_id)
    
    usd_to_exchange -= order.size * order.price
    btc_to_send += order.size
    bidasks.subtract(book.Book(bids=[order], asks=[]))

  logging.info("negligible usd left: %s" % usd_to_exchange)
  logging.info("btc to receive: %s" % btc_to_send)

  # check to make sure all orders are filled
  while True:
    try:
      if all(bitfloor.order_details(o_id)[u'status'] == 'filled' for o_id in order_ids):
        logging.info("SUCCESS!")
        break
    except HTTPError as e:
      logging.warn(e.message)
      time.sleep(0.5)

  # get coin cost
  coin_cost = Decimal('0')
  for o_id in order_ids:
    fills = bitfloor.order_details(o_id)[u'fills']
    for fill in fills:
      coin_cost += Decimal(fill[u'size']) * Decimal(fill[u'price']) + Decimal(fill[u'fee'])
  coin_cost = bitfloor.round_inc(coin_cost)

  return btc_to_send, coin_cost

def send_btc(to_addr, amount):
  # send btc from bitfloor to new wallet addr
  bitfloor.withdraw_btc(to_addr, amount)
  logging.info("sent %s btc from bitfloor to %s" % (amount, new_addr))
