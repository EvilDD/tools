
import pymysql


class mySql(object):
    """操作数据库"""

    def __init__(self):
        self.conn = pymysql.connect(
            database='crawler',
            user='root',
            password='123abc',
            host='45.78.62.18',  # localhost
            port=3306
        )
        self.cur = self.conn.cursor()

    def clearTable(self, table):
        order = 'TRUNCATE %s' % table
        self.cur.execute(order)
        self.conn.commit()
        self.closeMysql()

    def insertData(self, ipMes):  # 批量插数据
        order = 'INSERT INTO webIp (ip,port,type,area,timeout) VALUES (%s,%s,%s,%s,%s);'
        self.cur.executemany(order, ipMes)
        self.conn.commit()
        self.closeMysql()

    def closeMysql(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    mysql = mySql()
    # mysql.test()
