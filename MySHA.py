# coding=utf-8
from Gen_h import *
from functools import partial
import os


def read_file(file_path):
    # 判断路径文件存在
    if not os.path.isfile(file_path):
        raise TypeError(file_path + " does not exist")

    all_the_text = open(file_path).read()
    return all_the_text


def write_file(content, file_path):
    f = open(file_path, "w")
    j = 0
    for i in content:
        print >>f, i,
        j += 1
        if j % 10 == 0:
            print >>f, '\n'
    print 'success'
    f.close()


class SHA(object):

    __hex_bin = {
        '0': '0000', '1': '0001', '2': '0010', '3': '0011',
        '4': '0100', '5': '0101', '6': '0110', '7': '0111',
        '8': '1000', '9': '1001', 'a': '1010', 'b': '1011',
        'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111',
    }

    __F = lambda self, x, y: ''.join('0' if x[i] == y[i] else '1' for i in range(len(x)))  # 异或运算

    __A = lambda self, x, y: ''.join('1' if x[i] == '1' and y[i] == '1' else '0' for i in range(len(x)))  #与运算

    __L_X = lambda self, x, y: x[y:512] + x[0:y]  # 将x左位移y位

    __R_X = lambda self, x, y: x[512-y:512] + x[0:512-y]  # 将x右位移y位

    __E = lambda self, x, y: x + '0' * (128 - len(bin(y).split('b')[1])) + bin(y).split('b')[1]  # 用128位来表示y的数值，补充在x后

    __BX = partial(lambda y, x: ''.join(y[j] for j in ''.join('%02x' % ord(i) for i in x)), __hex_bin)

    __B = lambda self, x: ''.join('%02x' % ord(j) for j in x)

    def __init__(self):
        pass

    def s(self, x):
        e = len(x) % 1024 % 896
        if e == 1:
            x += '1'
        elif e > 1:
            x += '1' + '0' * (896 - e - 1)
        return self.__E(x, e)

    def add_mode(self, x, y):  # 64位的x与y的和模运算
        j = 0
        r = ''
        for i in range(len(x)):
            r += str((int(x[63-i]) + int(y[63-i]) + j) % 2)
            j = (int(x[63-i]) + int(y[63-i]) + j) / 2
        return r[::-1]

    def code(self, x):  # 定义一个接口
        x = self.s(x)
        h = form_h(8)
        c = ''
        for i in range(len(x) / 1024):  # 将init分组；
            l, r = x[1024 * i: 1024 * i + 512], x[1024 * i + 512: (i + 1) * 1024]
            l = self.__F(l, h)
            r = self.__A(r, h)
            l = self.__L_X(l, (i * 64) % 512)
            r = self.__R_X(r, (i * 64) % 512)
            x_t = self.__F(l, r)
            h_t = ''
            for j in range(8):
                x_i = x_t[64 * j: 64 * j + 64]
                h_i = h[64 * j: 64 * j + 64]
                h_t += (self.add_mode(x_i, h_i))
        for i in range(0, len(h_t), 4):
            c += hex(int(h_t[i:i+4], 2)).split('x')[1]
        return c
