from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
import base64

class RsaUtil:
    def __init__(self, pub_key, pri_key, pub_key_2):
        self.pri_key_obj = None
        self.pub_key_obj = None
        self.pub_key_obj_2 = None
        self.verifier = None
        self.signer = None
        if pub_key:
            pub_key = RSA.importKey(base64.b64decode(pub_key))
            self.pub_key_obj = Cipher_pkcs1_v1_5.new(pub_key)
            self.verifier = Signature_pkcs1_v1_5.new(pub_key)
        if pri_key:
            pri_key = RSA.importKey(base64.b64decode(pri_key))
            self.pri_key_obj = Cipher_pkcs1_v1_5.new(pri_key)
            self.signer = Signature_pkcs1_v1_5.new(pri_key)
        if pub_key_2:
            pub_key_2 = RSA.importKey(base64.b64decode(pub_key_2))
            self.pub_key_obj_2 = Cipher_pkcs1_v1_5.new(pub_key_2)
            self.verifier = Signature_pkcs1_v1_5.new(pub_key_2)

    def public_long_encrypt(self, data, charset='utf-8'):
        data = data.encode(charset)
        length = len(data)
        default_length = 117
        res = []
        for i in range(0, length, default_length):
            res.append(self.pub_key_obj.encrypt(data[i:i + default_length]))
        byte_data = b''.join(res)
        return base64.b64encode(byte_data)

    def private_long_decrypt(self, data, sentinel=b'decrypt error'):
        data = base64.b64decode(data)
        length = len(data)
        default_length = 128
        res = []
        for i in range(0, length, default_length):
            res.append(self.pri_key_obj.decrypt(data[i:i + default_length], sentinel))
        return str(b''.join(res), encoding = "utf-8")

    def sign(self, data, charset='utf-8'):
        h = SHA256.new(data.encode(charset))
        signature = self.signer.sign(h)
        return base64.b64encode(signature)

    def verify(self, data, sign,  charset='utf-8'):
        h = SHA256.new(data.encode(charset))
        return self.verifier.verify(h, base64.b64decode(sign))