# coding= utf-8
from MyRSA import RSA
from MyDES import DES
from MySHA import SHA


class Message(object):

    def encode_msg(self, x, ks, ku):
        ks = str(ks)
        d = DES()
        d.input_key(ks)
        s = SHA()
        r = RSA()
        sha = s.code(x)
        msg = d.encode(x)
        key = r.encrypt(ks, ku)
        return msg + " " + sha + " " + str(key)

    def encode_s_msg(self, x, ks):
        d = DES()
        d.input_key(ks)
        s = SHA()
        sha = s.code(x)
        msg = d.encode(x)
        return msg + " " + sha

    def decode_s_msg(self, x, ks):
        des, sha = x.split(" ")
        d = DES()
        s = SHA()
        ks = str(ks)
        d.input_key(ks)
        msg = d.decode(des)
        sha_v = s.code(msg)
        if sha_v != sha:
            msg = "msg had been changed!"
        return msg

    def decode_c_msg(self, x, pri):
        data, sha, key = x.split(" ")
        r = RSA()
        key = str(r.decrypt(int(key), pri))
        d = DES()
        d.input_key(key)
        data = str(data)
        data = d.decode(data).split()
        return data, key
