"""
 Bismuth Paper Wallet Seed Reader
 Version 0.1 Test Version
 Date 01/04/2018
 Copyright maccaspacca and jimhsu 2018
 Copyright The Bismuth Foundation 2016 to 2018
 Author Maccaspacca
 
 Reads the 24-word mnemonic seed from the paper wallet and recreates the address and the privkey.der / pubkey.der files
 Usage - python read_paper_bis.python
 make sure you have the mnemonic seed available and type in when prompted
 if you used a passphrase when you created the wallet then enter this when prompted
 the files are created in a folder named with the address name 
"""

import os, logging, pathlib, string, hashlib, time, base64
from logging.handlers import RotatingFileHandler
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
from libs.rsa_py import rsa_functions

# setup logging

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = 'read_paper.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

# some predefined variables to keep parity with jimhsu code

iterations = 20000
length = 48
n = 4096
cointype = 209 # Provisionally, 209 (atomic weight of bismuth) (see https://github.com/satoshilabs/slips/blob/master/slip-0044.md )
aid = 1
addrs = 1

# key reading

address = ""
	
pwd_a = input("Enter your 24 word mnemonic seed:\n")
app_log.info("Mnemonic (seed) = {}".format(pwd_a))

passphrase = input("Enter the passphrase you used (hit return for empty): ")
passP = "mnemonic" + passphrase

master_key = PBKDF2(pwd_a.encode('utf-8'), passP.encode('utf-8'), dkLen=length, count=iterations)
#print("Master key: " + str(base64.b64encode(master_key)))

deriv_path = "m/44'/"+ str(cointype) +"'/" + str(aid) + "/0/" + str(addrs) #HD path

account_key = PBKDF2(master_key, deriv_path.encode('utf-8'), dkLen=length, count=1)
#print("Account key: " + str(base64.b64encode(account_key)))

rsa = rsa_functions.RSAPy(n,account_key)
key = RSA.construct(rsa.keypair)

#public_key = key.publickey()

private_key_readable = key.exportKey().decode("utf-8")
public_key_readable = key.publickey().exportKey().decode("utf-8")
address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key

pathlib.Path(address).mkdir(parents=True, exist_ok=True) # create folder to store the files

app_log.info('Generating address: ' + address)
# generate key pair and an address

app_log.info("Client: Your address: " + str(address))
#app_log.info("Client: Your private key: " + str(private_key_readable))
#app_log.info("Client: Your public key: " + str(public_key_readable))

# created files

pem_file = open("{}/privkey.der".format(address), 'a')
pem_file.write(str(private_key_readable))
pem_file.close()

pem_file = open("{}/pubkey.der".format(address), 'a')
pem_file.write(str(public_key_readable))
pem_file.close()

address_file = open("{}/address.txt".format(address), 'a')
address_file.write(str(address) + "\n")
address_file.close()
