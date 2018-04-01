"""
 Bismuth Paper Wallet Address Generator Testing
 Version 0.1 Test Version
 Date 01/04/2018
 Copyright maccaspacca and jimhsu 2018
 Copyright The Bismuth Foundation 2016 to 2018
 Author Maccaspacca
 
 Test paper wallet deterministic address generation
 100 addresses are generated deterministically
 The deterministic word list is then used again
 and the resulting address compaired with the original
 if the addresses are the same then we have success
 the test should result on 100% success 
"""

import os, logging, pathlib, string, hashlib, time
from logging.handlers import RotatingFileHandler
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
from libs.mnemonic import Mnemonic
from libs.rsa_py import rsa_functions

# setup logging

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = 'test.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

# some predefined variables to keep parity with jimhsu code

mnemo = Mnemonic('english')
iterations = 20000
length = 48
n = 4096
cointype = 209 # Provisionally, 209 (atomic weight of bismuth) (see https://github.com/satoshilabs/slips/blob/master/slip-0044.md )
aid = 1
addrs = 1

# key generation

count = 1

test_file = open('testfile.txt', 'a')

while count < 101:

	address = ""
	pwd_a = mnemo.generate(strength=256)
	
	app_log.info("Mnemonic (seed) = {}".format(pwd_a))
	passphrase = ""
	passP = "mnemonic" + passphrase
	
	master_key = PBKDF2(pwd_a.encode('utf-8'), passP.encode('utf-8'), dkLen=length, count=iterations)
	
	deriv_path = "m/44'/"+ str(cointype) +"'/" + str(aid) + "/0/" + str(addrs) #HD path

	account_key = PBKDF2(master_key, deriv_path.encode('utf-8'), dkLen=length, count=1)
	
	rsa = rsa_functions.RSAPy(n,account_key)
	key = RSA.construct(rsa.keypair)
	
	private_key_readable = key.exportKey().decode("utf-8")
	public_key_readable = key.publickey().exportKey().decode("utf-8")
	address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key
	
	if (len(public_key_readable)) != 271 and (len(public_key_readable)) != 799:
		app_log.info('Generation fail pubkey {} : {}'.format(str(len(public_key_readable)),address))
	else:
		app_log.info('Generation success: {}'.format(address))
		test_file.write("{}:{}\n".format(address,pwd_a))
		count +=1

test_file.close()

# key testing

address = ""

with open('testfile.txt') as file:
	for line in file:
		line = line.strip() #preprocess line
		testline = line.split(":")
		test_address = testline[0]
		pwd_a = testline[1]
		
		passphrase = ""
		passP = "mnemonic" + passphrase
		
		master_key = PBKDF2(pwd_a.encode('utf-8'), passP.encode('utf-8'), dkLen=length, count=iterations)
		
		deriv_path = "m/44'/"+ str(cointype) +"'/" + str(aid) + "/0/" + str(addrs) #HD path

		account_key = PBKDF2(master_key, deriv_path.encode('utf-8'), dkLen=length, count=1)
		
		rsa = rsa_functions.RSAPy(n,account_key)
		key = RSA.construct(rsa.keypair)

		#private_key_readable = key.exportKey().decode("utf-8")
		public_key_readable = key.publickey().exportKey().decode("utf-8")
		address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key
		
		if address == test_address:
			app_log.info('Test re-key success: {}'.format(test_address))
		else:
			app_log.info('Test re-key failure: {}'.format(test_address))
