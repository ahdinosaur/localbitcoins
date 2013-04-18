from decimal import Decimal

import requests

import main
import bitfloor
import config.bitfloor
import config.blockchain
import utils

bitfloor = bitfloor.RAPI(product_id=1, key=config.bitfloor.key, secret=config.bitfloor.secret)

def send_btc(user_addr, amount):
  amount = Decimal(amount)
  print "sending %s btc to %s" % (amount, user_addr)
  if utils.yesornoquestion("are you sure this is correct?", default=True):
    # generate new blockchain.info wallet addr
    r = requests.get("https://blockchain.info/merchant/%s/new_address?password=%s&second_password=%s"
        % (config.blockchain.guid, config.blockchain.main_password, config.blockchain.second_password))
    r.raise_for_status()
    new_addr = r.json()['address']
    print "generated new address %s" % new_addr

    # send btc from bitfloor to new wallet addr
    bitfloor.withdraw_btc(new_addr, amount)
    print "sent %s btc from bitfloor to %s" % (amount, new_addr)

    # send btc from wallet to user
    r = requests.get("https://blockchain.info/merchant/%s/payment?password=%s&second_password=%s&to=%s&amount=%s&shared=%s"
        % (config.blockchain.guid, config.blockchain.main_password, config.blockchain.second_password, user_addr, int(Decimal(100000000) * amount), config.blockchain.shared))
    r.raise_for_status()
    print r.json()
    print "sent %s btc from wallet to %s" % (amount, user_addr)
  else:
    print "retrying"
    main.send_coins(amount)
