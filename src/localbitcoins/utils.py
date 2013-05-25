import sys
from hashlib import sha256
import re
import logging
logger = logging.getLogger("localbitcoins")
import sys

from qrtools import QR

qr = QR()
digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
 
def decode_base58(bc, length):
    n = 0
    for char in bc:
        n = n * 58 + digits58.index(char)

    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).decode('hex')
    # if length > len(s), add 0 padding
    for i in range(length - len(s)):
      s = '\x00' + s
    return s
 
def is_valid_btc_address(addr):
    bcbytes = decode_base58(addr, 25)
    return bcbytes[-4:] == sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]

def prompt(desc, validation):
    # get input
    inpt = raw_input("%s\n-> " % desc)

    # validate the input
    try:
        valid = re.match(validation, inpt)
    except TypeError:
        valid = validation(inpt)

    # if the input is valid, return it
    if valid:
        return inpt
    else:
        warn("that answer is invalid, try again")
        return prompt(desc, validation)

def warn(warn_msg):
    sys.stderr.write("WARNING: " + warn_msg + "\n")

def error(error_msg, exit_code=None):
    sys.stderr.write("ERROR: " + error_msg + "\n")
    if exit_code:
        sys.exit(exit_code)
    else:
        sys.exit(-1)

def yesornoquestion(question, default=None):
    if default:
        yesorno = raw_input(question + " [*'yes'* / 'no'] ")
    elif default == False:
        yesorno = raw_input(question + " ['yes' / *'no'*] ")
    else:
        yesorno = raw_input(question + " ['yes' / 'no'] ")

    if yesorno == "yes":
        return True
    elif yesorno == "no":
        return False
    elif yesorno == "" and default != None:
        return default
    else:
        sys.stderr.write("please answer either 'yes' or 'no'\n")
        return yesornoquestion(question)

def qr_for_address(callback):
  def check_addr_then_cb(s):
    if s.startswith("bitcoin:"):
      addr = re.split("bitcoin:",s)[1]
    else:
      addr = s
    if is_valid_btc_address(addr):
      callback(addr)
    else:
      warn("that address is invalid, try again")
      qr_for_address(callback)
  qr.decode_webcam(callback=check_addr_then_cb)

def prompt_for_addr(callback):
  address_method = prompt("copypaste or qrcode?", "(copypaste|qrcode)")
  if address_method == 'copypaste':
    to_addr = prompt("what address should i send the coins to?", is_valid_btc_address)
    callback(to_addr)
  elif address_method == 'qrcode':
    qr_for_address(callback)


if __name__ == '__main__':
  prompt_for_addr(lambda s: sys.stdout.write(s))

