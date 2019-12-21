import typing
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5

class Cipher:
    def __init__(self, pub_key_path: str, pri_key_path: str, pub_key_path2: str) -> None:
        self.pub_key_path = pub_key_path
        self.pri_key_path = pri_key_path
        self.pub_key_path2 = pub_key_path2
        with open(pub_key_path, 'r') as my_pub:
            self.pub_key = RSA.importKey(my_pub.read())
        with open(pri_key_path, 'r') as my_pri:
            self.pri_key = RSA.importKey(my_pri.read())
        with open(pub_key_path2, 'r') as other_pub:
            self.other_pub_key = RSA.importKey(other_pub.read())

    def encode(self, bs: bytearray):
        pass

    def decode(self):
        pass

    @classmethod
    def NewCipher(cls, pub_path: str, pri_path: str, pub_path2: str):
        return cls(pub_path, pri_path, pub_path2)
