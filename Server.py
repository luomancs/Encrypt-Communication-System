# coding=utf-8
import cPickle
import struct
import MySQLdb
import select
import signal
from socket import *
from Message import Message
from MyRSA import RSA
import random

HOST = ''


def send(channel, *arg):
    _buffer = cPickle.dumps(arg)
    value = htonl(len(_buffer))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(_buffer)


def receive(channel):
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = ntohl(struct.unpack("L", size)[0])
    except struct.error, e:
        return ''
    buf = ''
    while len(buf) < size:
        buf += channel.recv(size-len(buf))
    return cPickle.loads(buf)[0]


class Server(object):

    def __init__(self, PORT, backlog=5):
        self.client = {}
        self.clientMap = {}
        self.outputs = []
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 重用套接字地址
        self.server.bind((HOST, PORT))
        self.server.listen(backlog)
        self.client_id = []
        self.clients = 0
        self.ku = {}
        self.pri = (89951, 8123)
        self.pub = (89951, 11)
        self.message = Message()
        signal.signal(signal.SIGINT, self.signalhandler)

    def signalhandler(self, signum, frame):
        print "Shutting down server..."
        for output in self.outputs:
            output.close()
        self.server.close()

    def run(self):
        conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='20161024', db='networkSecurity')
        cur = conn.cursor()
        inputs = [self.server]
        print "Wait for connect...."
        while True:
            wait = True
            readable, writeable, exception = select.select(inputs, self.outputs, [])
            if wait:
                for sock in readable:
                    if sock is self.server:
                        client, address = self.server.accept()
                        data = receive(client)
                        data = self.message.decode_c_msg(data, self.pri)
                        data, ks = data[0], data[1]
                        cname = data[0]
                        pwd = data[1]
                        data_amount = cur.execute("select * from user where id=%s", [cname])
                        login = 0
                        if data_amount == 0:
                            register = RSA()
                            e, d, n = register.generate_keys(cname, pwd)
                            msg = str((str(e), str(d), str(n)))
                            print "connection from", address, cname
                            login = 1
                            self.ku[client] = (int(n), int(e))
                        else:
                            result = cur.fetchall()
                            if result[0][0] == cname and result[0][1] != pwd:
                                msg = str("wrong password!")
                            else:
                                msg = str([result[0][2], result[0][3], result[0][4]])
                                print "connection from", address, cname
                                login = 1
                                self.ku[client] = (int(result[0][4]), int(result[0][2]))
                        msg = self.message.encode_s_msg(msg, ks)
                        send(client, msg)
                        self.clients += 1
                        self.clientMap[cname] = client
                        self.client[client] = cname
                        if login:
                            for output in self.outputs:
                                name = self.client[output]
                                msg1 = "new connection from" + " " + str(cname)
                                ks = random.randint(0, 100)
                                pub = self.ku[output]
                                id = self.client[output]
                                msg1 = self.message.encode_msg(msg1, ks, pub)
                                send(output, msg1)
                                msg += name + " "
                            self.outputs.append(client)
                            inputs.append(client)
                    else:
                        try:
                            data = receive(sock)
                            if data:
                                data = self.message.decode_c_msg(data, self.pri)
                                send_id = self.client[sock]
                                rec_id = data[0][0]
                                content = data[0][1]
                                if rec_id in self.clientMap:
                                    rec_client = self.clientMap[rec_id]
                                    for output in self.outputs:
                                        if output == rec_client:
                                            ks = random.randint(0, 100)
                                            pub = self.ku[output]
                                            msg = send_id + ":" + content
                                            print send_id + " send message to " + rec_id + ": " + content
                                            msg = self.message.encode_msg(msg, ks, pub)
                                            send(output, msg)
                                            break
                                else:
                                    ks = random.randint(0, 100)
                                    pub = self.ku[sock]
                                    msg = rec_id + ":" + "not login"
                                    print msg
                                    msg = self.message.encode_msg(msg, ks, pub)
                                    send(sock, msg)
                            else:
                                if sock in inputs:
                                    self.clients -= 1
                                    inputs.remove(sock)
                                    self.outputs.remove(sock)
                        except error, e:
                            if sock in inputs:
                                inputs.remove(sock)
                                self.outputs.remove(sock)
        self.server.close()
if __name__ == "__main__":
    server = Server(6004)
    server.run()










