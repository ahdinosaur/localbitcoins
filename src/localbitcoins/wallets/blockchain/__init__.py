from decimal import Decimal

import requests
import logging
from ... import utils

import config

def receive_btc():
  """generates a Bitcoin receiving address"""
  # generate new blockchain.info wallet addr
  r = requests.get("https://blockchain.info/merchant/%s/new_address?password=%s&second_password=%s"
      % (config.guid, config.main_password, config.second_password))
  r.raise_for_status()
  new_addr = r.json()['address']
  print "generated new address %s" % new_addr
  return new_addr

def send_btc(to_addr, amount):
  amount = Decimal(amount)

  print "sending %s btc to %s" % (amount, to_addr)
  if utils.yesornoquestion("are you sure this is correct?", default=True):

    # send btc from wallet to user
    r = requests.get("https://blockchain.info/merchant/%s/payment?password=%s&second_password=%s&to=%s&amount=%s&shared=%s"
        % (config.guid, config.main_password, config.second_password, to_addr, int(Decimal(100000000) * amount), config.shared))
    r.raise_for_status()
    print r.json()
    print "sent %s btc from wallet to %s" % (amount, to_addr)
  else:
    print "retrying"
    main.send_coins(amount)

