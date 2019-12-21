from Crypto.Cipher import AES
import os

def AESPad(s: bytes) -> bytes:
    length = len(s)
    pad = b' '
    if (length % 16) == 0:
        s = s + pad * 15 + chr(16).encode()
    else:
        padding_num = 16 - (length % 16)
        s = s + (padding_num - 1) * pad + chr(padding_num).encode()
    return s

def AESDePad(s: bytes) -> bytes:
    padding_num = s[-1]
    return s[:-padding_num]

def EncodeAES(c: AES, s: bytes) -> bytes:
    return c.encrypt(AESPad(s))

def DecodeAES(c: AES, e: bytes) -> bytes:
    return AESDePad(c.decrypt(e))
 
# generate a random secret key
# secret = os.urandom(16)
 
# create a cipher object using the random secret
# cipher = AES.new(secret)
 
# encode a string
# encoded = EncodeAES(cipher, b'passwordi123longer')
# print('Encrypted string:', encoded)
 
# decode the encoded string
# decoded = DecodeAES(cipher, encoded)
# print('Decrypted string:', decoded)