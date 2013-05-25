from decimal import Decimal

from bitcoinrpc import ServiceProxy
import logging
from ... import utils

import config

access = ServiceProxy("http://%s:%s@localhost:8332")

def receive_btc():
  """generates a Bitcoin receiving address"""
  # generate new blockchain.info wallet addr
  new_addr = ""
  return new_addr

def send_btc(to_addr, amount):
  amount = Decimal(amount)

  print "sending %s btc to %s" % (amount, to_addr)
  if utils.yesornoquestion("are you sure this is correct?", default=True):

    # send btc from wallet to user
    print "sent %s btc from wallet to %s" % (amount, to_addr)
  else:
    print "retrying"
    send_btc(to_addr, amount)

