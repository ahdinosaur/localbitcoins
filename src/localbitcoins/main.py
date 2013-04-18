import time
from decimal import Decimal

from requests.exceptions import HTTPError

import bitfloor
import config.bitfloor
import config.preferences
import book
import ledger
import wallet
import utils

bitfloor = bitfloor.RAPI(product_id=1, key=config.bitfloor.key, secret=config.bitfloor.secret)

def get_coins(usd_to_exchange):
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

    print "there are %s bitcoins available at %s/btc" % (ask.size, ask.price)
    
    if ask.price * ask.size <= usd_to_exchange:
      order = book.Order(ask.size, bitfloor.floor_inc(ask.price))
    else:
      order = book.Order(bitfloor.floor_inc(usd_to_exchange / ask.price), bitfloor.floor_inc(ask.price))

    if order.size < 0.00001:
      break
    print "buying %s bitcoins at %s/btc" % (order.size, order.price)

    try:
      resp = bitfloor.buy(size=order.size, price=order.price)
    except HTTPError as e:
      print "error: %s" % e.message
      print "negligible usd left: %s" % usd_to_exchange
      print "btc to receive: %s" % btc_to_send
      time.sleep(1)
      continue

    order_id = resp[u'order_id']
    order_ids.append(order_id)
    
    usd_to_exchange -= order.size * order.price
    btc_to_send += order.size
    bidasks.subtract(book.Book(bids=[order], asks=[]))

  print "negligible usd left: %s" % usd_to_exchange
  print "btc to receive: %s" % btc_to_send

  # check to make sure all orders are filled
  while True:
    try:
      if all(bitfloor.order_details(o_id)[u'status'] == 'filled' for o_id in order_ids):
        print "SUCCESS!"
        break
    except HTTPError:
      print "waiting..."
      time.sleep(0.5)

  # get coin cost
  coin_cost = Decimal('0')
  for o_id in order_ids:
    fills = bitfloor.order_details(o_id)[u'fills']
    for fill in fills:
      coin_cost += Decimal(fill[u'size']) * Decimal(fill[u'price']) + Decimal(fill[u'fee'])
  coin_cost = bitfloor.round_inc(coin_cost)

  return btc_to_send, coin_cost

def send_coins(btc_to_send):
  address_method = utils.prompt("copypaste or qrcode?", "(copypaste|qrcode)")
  if address_method == 'copypaste':
    user_addr = utils.prompt("what address should i send the coins to?", utils.is_valid_btc_address)
    wallet.send_btc(user_addr, btc_to_send)
  elif address_method == 'qrcode':
    utils.qr_for_address(lambda s: wallet.send_btc(s, btc_to_send))


def main():
  # prompt user for how many usd to exchange
  usd_to_receive = Decimal(raw_input("how much usd do you want to exchange? "))
  # subtract fee
  fee = Decimal('1') - (Decimal('1') / (Decimal('1') + Decimal(config.bitfloor.account_deposit_fee) + Decimal(config.bitfloor.market_order_fee) + Decimal(config.preferences.commission)))
  usd_to_exchange = usd_to_receive * (Decimal('1') - fee)

  btc_to_send, coin_cost = get_coins(usd_to_exchange)

  # log exchange
  print "market cost to buy coins: %s" % coin_cost
  print "revenue to sell coins: %s" % usd_to_receive
  print "profit not including account deposit fees: %s" % (usd_to_receive - coin_cost)
  ledger.log(usd_to_receive, btc_to_send, coin_cost)

  # send user btc
  # prompt user for btc address to send coins to
  send_coins(btc_to_send)

