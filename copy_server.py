# coding=utf-8
import sys
import struct  # 将字符串打包为二进制流进行网络传输
import select  #
import signal  # 用于捕获中断信号
import cPickle  # 将python对象进行序列化:dumps将python对象序列化保存为字符串,loads与之相反
import MySQLdb
from socket import *
from MyRSA import RSA
from MyDES import DES
from MySHA import SHA
from Message import Message

HOST = ''


def send(channel, *args):  # 发送数据
    buffer = cPickle.dumps(args)
    value = htonl(len(buffer))
    size = struct.pack("L", value)
    channel.send(size)
    channel.send(buffer)


def receive(channel):  # 接收数据
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = ntohl(struct.unpack("L", size)[0])  # socket.ntohl(参考：http://blog.csdn.net/tatun/article/details/7194973)
    except struct.error, e:
        return ''
    buf = ''
    while len(buf) < size:
        buf += channel.recv(size - len(buf))
    return cPickle.loads(buf)[0]  # 恢复python对象


class ChatServer(object):
    def __init__(self, PORT, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []  # Client会话列表
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # 重用套接字地址
        self.server.bind((HOST, PORT))
        self.server.listen(backlog)
        signal.signal(signal.SIGINT,
                      self.signalhandler)  # 使用signal模块捕获中断操作 SIGINT中断进程(ctrl+c)， SIGTERM 终止进程，SIGKILL杀死进程，SIGALRM 闹钟信号

    def signalhandler(self, signum, frame):  # 中断处理方法
        print "Shutting down server ..."
        for output in self.outputs:
            output.close()
        self.server.close()

    def get_client_name(self, client):
        info = self.clientmap[client]
        host, port, name = info[0][0], info[0][1], info[1]
        return ':'.join((('@'.join((name, host))), str(port)))

    def run(self):

        conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='20161024', db='networkSecurity')
        cur = conn.cursor()
        inputs = [self.server]
        print 'Waiting for connect...'
        while True:
            try:
                readable, writeable, execption = select.select(inputs, self.outputs, [])
            except select.error, e:
                break
            for sock in readable:
                if sock == self.server:  # 服务器端接收
                    client, address = self.server.accept()
                    # 获得Client端发送的消息
                    try:
                        data, sha, key = receive(client).split(" ")
                    except:
                        d = DES()
                        d.input_key(key)
                        msg = d.encode(msg) + " " + sha
                        send(client, msg)
                    r = RSA()
                    key = str(r.decrypt(int(key), (89951, 8123)))
                    d = DES()
                    d.input_key(key)
                    data = d.decode(data).split(" ")
                    cname = data[0]  # 账号
                    pwd = data[1]  # 密码
                    data_amount = cur.execute("select * from user where id=" + cname)
                    login_success = 0
                    if data_amount == 0:
                        register = RSA()
                        e, d, n = register.generate_keys(cname, pwd)
                        msg = str((e, d, n))
                        s = SHA()
                        sha = s.code(msg)
                        d = DES()
                        d.input_key(key)
                        msg = d.encode(msg) + " " + sha
                        send(client, msg)
                        login_success = 1
                    else:
                        result = cur.fetchall()
                        if result[0][0] == cname and result[0][1] != pwd:
                            msg = str("Wrong pwd!")
                            s = SHA()
                            sha = s.code(msg)
                            d = DES()
                            d.input_key(key)
                            msg = d.encode(msg) + " " + sha
                            send(client, msg)
                        else:
                            msg = str((result[0][2], result[0][3], result[0][4]))
                            s = SHA()
                            sha = s.code(msg)
                            d = DES()
                            d.input_key(key)
                            msg = d.encode(msg) + " " + sha
                            send(client, msg)
                            login_success = 1
                    if login_success == 1:
                        print "Chat server: connected from", address
                        self.clients += 1
                        send(client, str(address[0]))
                        inputs.append(client)
                        self.clientmap[client] = (address, cname)
                        msg = "(Connected : New Client(%d) from %s)\n" % (self.clients, self.get_client_name(client))
                        message = "At present, only one of you is in the chat room!"
                        if self.clients == 1:
                            send(client, message)
                        for output in self.outputs:
                            send(output, msg)
                        self.outputs.append(client)  # 将开始回话的client加入Client回话列表
                        # elif sock == sys.stdin:
                        # break
                else:
                    try:
                        data = receive(sock)
                        data, key = data.split(" ")
                        r = RSA()
                        key = str(r.decrypt(int(key), (89951, 8123)))
                        d = DES()
                        d.input_key(key)
                        data = d.decode(data)
                        if data:
                            data_split = data.split()
                            print data_split
                            if '注册'.decode('utf-8') == data_split[0]:
                                register = RSA()
                                pub, pri = register.generate_keys(data_split[1], data_split[2])
                                msg = str(pub) + str(pri)
                                print msg
                                for output in self.outputs:
                                    if output == sock:
                                        send(output, msg)
                        else:
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)
                            msg = '(Now hung up: Client from %s)' % self.get_client_name(sock)
                            message = "At present, only one of you is in the chat room!"
                            for output in self.outputs:
                                send(output, msg)
                            if self.clients == 1:
                                send(self.outputs[0], message)
                    except error, e:
                        inputs.remove(sock)
                        self.outputs.remove(sock)
        self.server.close()


if __name__ == "__main__":
    server = ChatServer(6004)
    server.run()


