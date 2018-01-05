#! /usr/bin python
import math
import random
import MySQLdb


class RSA(object):
    __prime_number = [101, 103, 107, 109, 113, 121, 127, 131, 137, 139, 143, 149,
                      151, 157, 163, 167, 169, 173, 179, 181, 191, 193, 197, 199,
                      211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271,
                      277, 281, 283, 289, 293, 307, 311, 313, 317, 323, 331, 337,
                      347, 349, 353, 359, 361, 367, 373, 379, 383, 389, 397, 401,
                      409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467,
                      479, 487, 491, 499, 503, 509, 521, 523, 529, 541, 547, 557,
                      563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619,
                      631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
                      709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787,
                      797, 809, 811, 821, 823, 827, 829, 839, 841, 853, 857, 859,
                      863, 877, 881, 883, 887, 899, 907, 911, 919, 929, 937, 941,
                      947, 953, 961, 967, 971, 977, 983, 991, 997]

    def range_prime(self, start, end):
        l = list()
        for i in range(start, end+1):
            flag = True
            for j in range(2, int(math.sqrt(i))):
                if i % j == 0:
                    flag = False
                    break
            if flag:
                l.append(i)
        return l

    def select_p_q(self):
        find_p_q = False
        conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='20161024', db='networkSecurity')
        cur = conn.cursor()
        # cur.execute("create table p_qTable(p int,q int)")
        while not find_p_q:
            p = self.__class__.__prime_number[random.randint(0, 152)]
            q = self.__class__.__prime_number[random.randint(0, 152)]
            sql = "select * from p_qTable where p = %s and q= %s"
            param = (p, q)
            if cur.execute(sql, param) == 0:
                find_p_q = True
                sql = "insert into p_qTable values (%s, %s)"
                cur.execute(sql, (p, q))
                conn.commit()
        conn.close()
        return p, q

    def generate_keys(self, id, pwd):
        conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='20161024', db='networkSecurity')
        cur = conn.cursor()
        p, q = self.select_p_q()
        N = p * q
        C = (p-1) * (q-1)
        number1 = self.range_prime(10, 100)
        number2 = range(2, C)
        e = 0
        for i in number1:
            if C % i > 0:
                e = i
                break
        if e == 0:
            raise StandardError("e not find")
        d = 0
        for i in number2:
            if (i * e) % C == 1:
                d = i
                break
        if d == 0:
            raise StandardError("d not find")
        sql = "insert into user values (%s, %s, %s, %s, %s)"
        cur.execute(sql, (id, pwd, e, d, N))
        conn.commit()
        conn.close()
        # return (N, e), (N, d)
        return e, d, N

    def encrypt(self, m, key):
        C, x = key
        m = int(m)
        C = int(C)
        x = int(x)
        return (m ** x) % C
    decrypt = encrypt
