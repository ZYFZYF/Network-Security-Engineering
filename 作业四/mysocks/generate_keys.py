from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from aes import EncodeAES, DecodeAES
import base64
import os

secret = os.urandom(16)
# create a cipher object using the random secret
cipher = AES.new(secret)
 
# encode a string
encoded = EncodeAES(cipher, b'passwordi123longer')
print('Encrypted string:', encoded)
 
# decode the encoded string
decoded = DecodeAES(cipher, encoded)
print('Decrypted string:', decoded)

# # 获取一个伪随机数生成器
random_generator = Random.new().read
# # 获取一个rsa算法对应的密钥对生成器实例
# rsa = RSA.generate(1024, random_generator)

# # 生成私钥并保存
# private_pem = rsa.exportKey()
# with open('rsa.key2', 'wb') as f:
#     f.write(private_pem)

# # 生成公钥并保存
# public_pem = rsa.publickey().exportKey()
# with open('rsa.pub2', 'wb') as f:
#     f.write(public_pem)

pub = open("rsa.pub", 'r')
pri = open("rsa.key", 'r')
pub_key = RSA.importKey(pub.read())
pri_key = RSA.importKey(pri.read())
pub.close()
pri.close()

string = b"a plain text"
cipher = Cipher_pkcs1_v1_5.new(pub_key)
# encoded_text = cipher.encrypt(string)
# ciphered_text = base64.b64encode(cipher.encrypt(string))
# print(encoded_text)

h = SHA256.new(string)
signer = Signature_pkcs1_v1_5.new(pri_key)
signature = signer.sign(h)
print(signature)

# print(len(encoded_text))
# print(len(signature))
# whole_package = encoded_text + signature
# print(len(whole_package))
# print(whole_package)

whole = string
print(whole)
print(len(whole))
whole = cipher.encrypt(whole)
print(whole)
whole_encoded = base64.urlsafe_b64encode(whole)
print(whole_encoded)

whole_decoded = base64.urlsafe_b64decode(whole_encoded)
print(whole_decoded)

decoder = Cipher_pkcs1_v1_5.new(pri_key)
decoded_string = decoder.decrypt(whole_decoded, random_generator)
print(decoded_string)
# print(base64.urlsafe_b64decode(encoded_text))
# print(base64.urlsafe_b64decode(signature))
# print(base64.urlsafe_b64decode(whole_package))

# whole_package = base64.urlsafe_b64decode(whole_package)
# print(len(whole_package))

# decoder = Cipher_pkcs1_v1_5.new(pri_key)
# decoded_text = decoder.decrypt(whole_package[:-128], random_generator)
# print(decoded_text)

# verifier = Signature_pkcs1_v1_5.new(pub_key)
# verified = verifier.verify(h, whole_package[128:])
# print(verified)