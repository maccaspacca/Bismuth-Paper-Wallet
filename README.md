# Bismuth-Paper-Wallet
Paper wallet creator for Bismuth

THIS VERSION IS FOR TEST ONLY DO NOT USE !!!

write_paper_bis.py

This writes your paper Bismuth wallet and saves it to PDF for printing or alternative storage. The files are created in a folder named with the address name.

Usage: python write_paper_bis.py
 
A deterministic key will be created using a random 24 word mnemonic seed. The key creation uses the same methods as used in 'Proof of concept deterministic RSA address generation for Bismuth'
see https://github.com/jimhsu/bis-hd-poc
 
The software will prompt for an optional passphrase as additional security - if you choose this option please be aware that this it NOT stored in the paper wallet

IF YOU FORGET THE PASSPHRASE YOU WILL LOSE YOUR BISMUTH
 
The wallet is saved as a PDF file together with the key files (for testing against a node). You can print the PDF out on a good quality laser printer and store in a secure location.

Note: test the key regeneration before sending any Bismuth to the address or detroying the key files.

read_paper_bis.py

Reads the 24-word mnemonic seed from the paper wallet and recreates the address and the privkey.der and pubkey.der files

Usage: python read_paper_bis.python

Make sure you have the mnemonic seed available and type in when prompted. If you used a passphrase when you created the wallet then also enter this when prompted.

The files are created in a folder named with the address name.

test.py

This can be used to test the key creation and regeneration code.

Usage: python test.py

100 addresses are generated deterministically. The deterministic word list is then used again and the resulting address compaired with the original.

If the addresses are the same then we have success

The test should result in 100% success
