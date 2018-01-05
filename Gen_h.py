# coding=utf-8
import math


def find_prime(x):
        l = 3
        list_t = [2]
        while len(list_t) < x:
            flag = True
            for i in range(2, l):
                if l % i == 0:
                    flag = False
                    break
            if flag:
                list_t.append(l)
            l += 1
        return list_t


def form_h(x):
        list_t = find_prime(int(x))
        x = ''
        for i in list_t:
            x += (str("%.64f" % math.sqrt(i)).split('.')[1])
        return x
