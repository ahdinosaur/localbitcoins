import hmac
import hashlib
import base64
import time
import copy
import urllib
from decimal import Decimal
import decimal
import os

import requests

import config.bitfloor

class RAPI(object):
  def __init__(self, product_id, key, secret):
    self._key = key
    self._secret = secret
    self._product_id = product_id
    self._inc = Decimal('0.0001') # TODO: get from bitfloor

  def book(self, level=1):
    url = '/book/L{1}/{0}'.format(self._product_id, level)
    return self._send_get(url)

  def ticker(self):
    url = '/ticker/{0}'.format(self._product_id)
    return self._send_get(url)

  def trades(self):
    url = '/history/{0}'.format(self._product_id)
    return self._send_get(url)

  def order_new(self, side, size, price):
    return self._send_post('/order/new', {
        'product_id': self._product_id,
        'side': side,
        'size': size,
        'price': price
    })

  def buy(self, **kwargs):
    return self.order_new(side=0, **kwargs)

  def sell(self, **kwargs):
    return self.order_new(side=1, **kwargs)

  def order_cancel(self, order_id):
    return self._send_post('/order/cancel', {
        'product_id': self._product_id,
        'order_id': order_id
    })

  def order_details(self, order_id):
    return self._send_post('/order/details', {
        'order_id': order_id
    })

  def withdraw(self, currency, amount, method, destination):
    return self._send_post('/withdraw', {
        'currency': currency,
        'amount': amount,
        'method': method,
        'destination': destination
    })

  def withdraw_btc(self, address, amount):
    return self.withdraw('BTC', amount, 'bitcoin', address)

  def orders(self):
    return self._send_post('/orders')

  def accounts(self):
    return self._send_post('/accounts')


  def floor_inc(self, n):
    return (Decimal(str(n))/self._inc).quantize(Decimal('1'), rounding=decimal.ROUND_DOWN)*self._inc

  def ceil_inc(self, n):
    return (Decimal(str(n))/self._inc).quantize(Decimal('1'), rounding=decimal.ROUND_UP)*self._inc

  def round_inc(self, n):
    return (Decimal(str(n))/self._inc).quantize(Decimal('1'))*self._inc

  def _send_get(self, url, payload={}):
    r = requests.get("%s%s" % (config.bitfloor.host, url), data=payload, verify=False)
    r.raise_for_status()
    return r.json()

  def _send_post(self, url, payload={}):
    payload = copy.copy(payload) # avoid modifying the original dict

    # add some stuff to the payload
    payload['nonce'] = int(time.time()*1e6)

    body = urllib.urlencode(payload)

    sig = hmac.new(base64.b64decode(self._secret), body, hashlib.sha512).digest()
    sig_b64 = base64.b64encode(sig)

    headers = {
        'bitfloor-key': self._key,
        'bitfloor-sign': sig_b64,
        'bitfloor-passphrase': config.bitfloor.passphrase,
        'bitfloor-version': config.bitfloor.version,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': len(body)
    }

    r = requests.post("%s%s" % (config.bitfloor.host, url), data=body, headers=headers, verify=False)
    r.raise_for_status()
    return r.json()
