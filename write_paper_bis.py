"""
 Bismuth Paper Wallet Generator
 Version 0.3 Test Version
 Date 10/04/2018
 Copyright maccaspacca and jimhsu 2018
 Copyright The Bismuth Foundation 2016 to 2018
 Author Maccaspacca
 
 Usage:
Basic paper wallet: python write_paper_bis.py
Full paper wallet including public and privkey storage: python write_paper_bis.py full
 
 A deterministic key will be created using a random 24 word mnemonic seed.
 The key creation uses the same methods as used in 'Proof of concept deterministic RSA address generation for Bismuth'
 see https://github.com/jimhsu/bis-hd-poc
 
 The software will prompt for an optional passphrase as additional security - if you choose this option please be aware that this it NOT stored in the paper wallet
 IF YOU FORGET THE PASSPHRASE YOU WILL LOSE YOUR BISMUTH
 
 The software will also ask you to optionally add a message (text) to be added to the first page.
 
 The wallet is saved as a PDF file together with the key files (for testing against a node)
 
 You can print the PDF out on a good quality laser printer and store in a secure location.
 test the key regeneration before sending any bismuth to the address or destroying the key files
"""

import os, logging, pathlib, string, hashlib, pyqrcode, fpdf, time, base64, sys
from logging.handlers import RotatingFileHandler
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
from libs.mnemonic import Mnemonic
from libs.rsa_py import rsa_functions

# pre-defined variables, classes and routines 

pubkey_txt = "Below are a number of QR code images which together form your public key. You should scan each one starting from the top and working your way down. Paste the text data into a file one after the other and then save the file as pubkey.der"
privkey_txt = "Below are a number of QR code images which together form your private key. You should scan each one starting from the top and working your way down. Paste the text data into a file one after the other and then save the file as privkey.der"

def do_more():
	try:
		if sys.argv[1]:
			my_arg = sys.argv[1].lower()
			if my_arg == "full":
				return True
			else:
				return False
	except:
		return False

def split_str(seq, chunk, skip_tail=False):
	lst = []
	if chunk <= len(seq):
		lst.extend([seq[:chunk]])
		lst.extend(split_str(seq[chunk:], chunk, skip_tail))
	elif not skip_tail and seq:
		lst.extend([seq])
	return lst

########################################################################
class MyPDF(fpdf.FPDF):
	""""""

	#----------------------------------------------------------------------
	def header(self):
		"""
		Header on each page
		"""
		# insert my logo
		self.image("icon.png", x=10, y=8, w=23)
		# position logo on the right
		self.cell(w=60)

		# set the font for the header, B=Bold
		self.set_font("Arial", style="B", size=15)
		# page title
		self.cell(80,10, "Bismuth Paper Wallet", border=0, ln=0, align="C")
		# insert a line break of 20 pixels
		self.ln(20)

	#----------------------------------------------------------------------
	def footer(self):
		"""
		Footer on each page
		"""
		# position footer at 15mm from the bottom
		self.set_y(-15)

		# set the font, I=italic
		self.set_font("Arial", style="I", size=8)

		# display the page number and center it
		pageNum = "Page %s/{nb}" % self.page_no()
		self.cell(0, 10, pageNum, align="C")
 
#----------------------------------------------------------------------

########################################################################

# setup logging

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = 'paper_write.log'
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

address = ""
pwd_a = mnemo.generate(strength=256)

app_log.info("Mnemonic (seed) = {}".format(pwd_a))
passphrase = input("Enter optional passphrase (hit return for empty): ")
opt_msg = input("Enter optional front page message (hit return for empty): ")
passP = "mnemonic" + passphrase

master_key = PBKDF2(pwd_a.encode('utf-8'), passP.encode('utf-8'), dkLen=length, count=iterations)
#print("Master key: " + str(base64.b64encode(master_key)))

deriv_path = "m/44'/"+ str(cointype) +"'/" + str(aid) + "'/0/" + str(addrs) #HD path

account_key = PBKDF2(master_key, deriv_path.encode('utf-8'), dkLen=length, count=1)
#print("Account key: " + str(base64.b64encode(account_key)))

rsa = rsa_functions.RSAPy(n,account_key)
key = RSA.construct(rsa.keypair)

private_key_readable = key.exportKey().decode("utf-8")
public_key_readable = key.publickey().exportKey().decode("utf-8")
address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key

pathlib.Path(address).mkdir(parents=True, exist_ok=True) # create folder to store the files

app_log.info('Generating address: ' + address)
# generate key pair and an address

pwd_qr = pyqrcode.create(pwd_a)
pwd_qr.png('pwd_qr.png', scale=5)

address_qr = pyqrcode.create(address)
address_qr.png('{}/address_qr.png'.format(address), scale=5)

##############################

# Create PDF

if do_more():
	my_size = "A4"
	my_orient = "P"
	
	pub_split = split_str(str(public_key_readable), 512)
	priv_split = split_str(str(private_key_readable), 512)

	p = 0
	for pub in pub_split:
		p +=1
		this_qr = pyqrcode.create(pub)
		this_qr.png('{}/pubkey_{}.png'.format(address,str(p)), scale=5)
		
	num_pubs = p
		
	p = 0
	for priv in priv_split:
		p +=1
		this_qr = pyqrcode.create(priv)
		this_qr.png('{}/privkey_{}.png'.format(address,str(p)), scale=5)

	num_privs = p

	p = 0
else:
	my_size = "A5"
	my_orient = "L"

pdf = MyPDF(my_orient,'mm',my_size)
pdf.set_font("Times", size=12)
pdf.alias_nb_pages()

pdf.add_page()
pdf.set_font("Times", style='B', size=12)
pdf.cell(200, 10, opt_msg, ln=1, align="C")

pdf.add_page()
pdf.set_font("Times", style='B', size=12)
pdf.cell(200, 10, txt="Wallet Address", ln=1, align="C")
pdf.cell(200,10,address,0,1,'C')
pdf.image('{}/address_qr.png'.format(address), x=70, y=60, w=75)

pdf.add_page()
pdf.set_font("Times", style='B', size=12)
pdf.cell(200, 10, txt="24-word mnemonic seed in BIP39 format", ln=1, align="C")
pdf.set_font("Times", style='B', size=14)
pdf.multi_cell(0,10,pwd_a,0,0,'J',False)
pdf.image('pwd_qr.png'.format(address), x=70, y=60, w=75)

if os.path.isfile("pwd_qr.png") is True:
	os.remove("pwd_qr.png")
	
if do_more():
	print("Print Full PDF")			
	pdf.add_page()
	pdf.set_font("Times", style='B', size=10)
	pdf.cell(200, 10, txt="Public Key Information", ln=1, align="C")
	pdf.multi_cell(0,10,pubkey_txt,0,0,'J',False)
	pdf.set_font("Times", size=8)
	for d in range(num_pubs):
		pdf.cell(0,4,'Scan number {}'.format(str(d+1)),0,1,'L')
		pdf.image("{}/pubkey_{}.png".format(address,str(d+1)),w=75)
		
	pdf.add_page()
	pdf.set_font("Times", size=8)
	pdf.ln(2)
	pdf.multi_cell(0,4,str(public_key_readable),0,0,'J',False)

	pdf.add_page()
	pdf.set_font("Times", style='B', size=12)
	pdf.cell(200, 10, txt="Private Key Information", ln=1, align="C")
	pdf.multi_cell(0,10,privkey_txt,0,0,'J',False)
	pdf.set_font("Times", size=8)
	for d in range(num_privs):
		pdf.cell(0,4,'Scan number {}'.format(str(d+1)),0,1,'L')
		pdf.image("{}/privkey_{}.png".format(address,str(d+1)),w=75)

	pdf.add_page()
	pdf.set_font("Times", size=8)
	pdf.ln(2)
	pdf.multi_cell(0,4,str(private_key_readable),0,0,'J',False)

else:
	print("Print Normal PDF")

pdf.output("{}/bis_{}.pdf".format(address,address))

################################################################

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
