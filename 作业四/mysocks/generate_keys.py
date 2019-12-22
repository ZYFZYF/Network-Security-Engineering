from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from aes import AESUtil
from rsa import RsaUtil
from cipher import Cipher
import base64
import os

cipher1 = Cipher("rsa.pub", "rsa.key", "rsa.pub2")
cipher2 = Cipher("rsa.pub2", "rsa.key2", "rsa.pub")
key = b'j(5\xf7!\xccv\xd8T\xf7\xa3\x9c\x13\xf9\x9e\xa0'
# key = cipher1.aes_util.GenerateKey()
cipher1.aes_util.SetKey(key)
cipher2.aes_util.SetKey(key)

text = os.urandom(1024)
print(text)
encoded = cipher1.encode(text)
print(encoded)
decoded = cipher2.decode(encoded)
print(decoded)
print(text==decoded)
print(len(text), len(encoded), len(decoded))