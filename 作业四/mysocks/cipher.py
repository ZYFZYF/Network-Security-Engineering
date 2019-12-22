import typing
import base64
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from rsa import RsaUtil
from aes import AESUtil

class VerifyFailed(Exception):
    """认证失败"""

class Cipher:
    def __init__(self, pub_key_path: str, pri_key_path: str, pub_key_path2: str) -> None:
        self.pub_key_path = pub_key_path
        self.pri_key_path = pri_key_path
        self.pub_key_path2 = pub_key_path2
        with open(pub_key_path, 'r') as my_pub:
            self.pub_key = my_pub.read()
        with open(pri_key_path, 'r') as my_pri:
            self.pri_key = my_pri.read()
        with open(pub_key_path2, 'r') as other_pub:
            self.pub_key_2 = other_pub.read()
        self.rsa_util = RsaUtil(self.pub_key, self.pri_key, self.pub_key_2)
        self.aes_util = AESUtil()

    def encode(self, bs: bytes):
        sign = self.rsa_util.sign(bs)
        message = bs + sign
        res = self.rsa_util.public_long_encrypt(message)
        res = self.aes_util.EncodeAES(res)
        res = base64.urlsafe_b64encode(res)
        return res

    def decode(self, message):
        message = base64.urlsafe_b64decode(message)
        message = self.aes_util.DecodeAES(message)
        message = self.rsa_util.private_long_decrypt(message)
        content = message[:-128]
        sign = message[-128:]
        verified = self.rsa_util.verify(content, sign)
        if not verified:
            raise VerifyFailed
        return content

    @classmethod
    def NewCipher(cls, pub_path: str, pri_path: str, pub_path2: str):
        return cls(pub_path, pri_path, pub_path2)

def main():
    cipher1 = Cipher("rsa.pub", "rsa.key", "rsa.pub2")
    cipher2 = Cipher("rsa.pub2", "rsa.key2", "rsa.pub")
    key = cipher1.aes_util.GenerateKey()
    cipher2.aes_util.SetKey(key)
    text = b"this is a new test"
    # sign = cipher1.rsa_util.sign(text)
    # print(sign, len(sign))
    # print(cipher2.rsa_util.verify(text, sign))
    # encoded = cipher1.aes_util.EncodeAES(text)
    # print(encoded)
    # decoded = cipher2.aes_util.DecodeAES(encoded)
    # print(decoded)
    encoded = cipher1.encode(text)
    print(encoded)
    decoded = cipher2.decode(encoded)
    print(decoded)

if __name__ == "__main__":
    main()