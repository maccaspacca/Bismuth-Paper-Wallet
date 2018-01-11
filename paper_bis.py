"""
 Bismuth Paper Wallet Generator
 Test Version 0.0.1
 Date 11/01/2018
 Copyright Maccaspacca 2018
 Copyright Hclivess 2016 to 2018
 Author Maccaspacca
"""

import os, sys, logging, pathlib
from logging.handlers import RotatingFileHandler
from Crypto import Random
#from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
#from Crypto.Signature import PKCS1_v1_5
import hashlib
import pyqrcode
import fpdf

pubkey_txt = "Below are a number of QR code images which together form your public key. You should scan each one starting from the top and working your way down. Paste the text data into a file one after the other and then save the file as pubkey.der"
privkey_txt = "Below are a number of QR code images which together form your private key. You should scan each one starting from the top and working your way down. Paste the text data into a file one after the other and then save the file as privkey.der"

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
		self.cell(60,10, "Bismuth Paper Wallet", border=0, ln=0, align="C")
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

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = 'keygen.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(message)s')
ch.setFormatter(formatter)
app_log.addHandler(ch)

# key maintenance
if os.path.isfile("privkey.der") is True:
	app_log.info("Client: privkey.der found")
else:
	address = ""

	# generate key pair and an address
	random_generator = Random.new().read
	key = RSA.generate(4096, random_generator)
	public_key = key.publickey()

	private_key_readable = key.exportKey().decode("utf-8")
	public_key_readable = key.publickey().exportKey().decode("utf-8")
	address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key
	
	pathlib.Path(address).mkdir(parents=True, exist_ok=True)

	app_log.info('Generating address: ' + address)
	# generate key pair and an address
	
	address_qr = pyqrcode.create(address)
	address_qr.png('{}/address_qr.png'.format(address))

	pub_split = split_str(str(public_key_readable), 512)
	priv_split = split_str(str(private_key_readable), 1024)

	p = 0
	for pub in pub_split:
		p +=1
		this_qr = pyqrcode.create(pub)
		this_qr.png('{}/pubkey_{}.png'.format(address,str(p)))
		
	num_pubs = p
		
	p = 0
	for priv in priv_split:
		p +=1
		this_qr = pyqrcode.create(priv)
		this_qr.png('{}/privkey_{}.png'.format(address,str(p)))

	num_privs = p
	
	p = 0
	
	pdf = MyPDF()
	pdf.set_font("Times", size=12)
	pdf.alias_nb_pages()
	
	pdf.add_page()
	pdf.set_font("Times", style='B', size=12)
	pdf.cell(200, 10, txt="Wallet Address", ln=1, align="C")
	pdf.cell(200,10,address,0,1,'C')
	pdf.image('{}/address_qr.png'.format(address), x=70, y=60, w=75)
	
	pdf.add_page()
	pdf.set_font("Times", style='B', size=12)
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
	
	pdf.output("{}/bis_{}.pdf".format(address,address))

	app_log.info("Client: Your address: " + str(address))
	#app_log.info("Client: Your private key: " + str(private_key_readable))
	#app_log.info("Client: Your public key: " + str(public_key_readable))

	pem_file = open("{}/privkey.der".format(address), 'a')
	pem_file.write(str(private_key_readable))
	pem_file.close()

	pem_file = open("{}/pubkey.der".format(address), 'a')
	pem_file.write(str(public_key_readable))
	pem_file.close()

	address_file = open("{}/address.txt".format(address), 'a')
	address_file.write(str(address) + "\n")
	address_file.close()
