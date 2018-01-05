# coding=utf-8
import MySQLdb


conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='20161024', db='networkSecurity')
cur = conn.cursor()

cur.execute("create table user(id VARCHAR(100),pwd VARCHAR(100),e VARCHAR(100),d VARCHAR(100),n VARCHAR(100))")


sql = "insert into p_qTable values (%s, %s)"
param = [5, 11]
#cur.execute(sql, param)


#修改查询条件的数据
sql = "insert into user values (%s, %s, (%s, %s), (%s, %s))"
pri = (1,1)
pub = (0,0)
#cur.execute(sql, (12345, 12345, (1, 1), (0, 0)))


cur.close()
conn.commit()
conn.close()

