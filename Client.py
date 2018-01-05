# coding=utf-8
from Server import send, receive
from socket import *
import select
import sys
from Message import Message
import random


class Client(object):
    def __init__(self, info):
        self.connection = False
        self.host = 'localhost'
        self.port = 6004
        self.message = Message()
        try:
            while True:
                self.sock = socket(AF_INET, SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                self.connection = True
                ks = random.randint(1, 100)
                info = self.message.encode_msg(info, ks, (89951, 11))
                send(self.sock, info)
                data = receive(self.sock)
                data = self.message.decode_s_msg(data, ks)
                if data == 'wrong password!' or data == 'msg had been changed!':
                    print data
                    info = raw_input("Please enter username and password > ")
                else:
                    print "login success!"
                    data = data.split("'")
                    e, d, n = data[1], data[3], data[5]
                    self.pub = (int(n), int(e))
                    self.pri = (int(n), int(d))
                    break
        except error, e:
            print 'Failed to connect to chat server'
            sys.exit(1)

    def run(self):
        while True:
            try:
                readable, writeable, exception = select.select([0, self.sock], [], [])

                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip()
                        if data:
                            ks = random.randint(1, 100)
                            data = self.message.encode_msg(data, ks, (89951, 11))
                            send(self.sock, data)
                    else:
                        data = receive(self.sock)
                        if not data:
                            self.connection = False
                            self.sock.close()
                            break
                        else:
                            try:
                                data = self.message.decode_c_msg(data, self.pri)
                                print " ".join(data[0])
                            except error, e:
                                print ""
            except KeyboardInterrupt, e:
                print 'Client interrupted'
                self.sock.close()
                break
if __name__ == "__main__":
    info = raw_input("Please enter username and password > ")
    client = Client(info)
    client.run()