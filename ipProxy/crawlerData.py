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

    def clearTable(self, table):  # 此处不能关闭数据库连接
        order = 'TRUNCATE %s' % table
        self.cur.execute(order)
        self.conn.commit()

    def insertData(self, ipMes):  # 批量插数据抓回来的ip所有数据
        order = 'INSERT INTO webIp (ip,port,type,area,timeout) VALUES (%s,%s,%s,%s,%s);'
        self.cur.executemany(order, ipMes)
        self.conn.commit()
        self.closeMysql()

    def insertUseIp(self, ipTime):  # 批量插入可用ip和超时时间
        order = 'INSERT INTO useIp (ipport,timeout) VALUES (%s,%s);'
        self.cur.executemany(order, ipTime)
        self.conn.commit()
        self.closeMysql()

    def selectIpPort(self, table):
        order = 'SELECT * FROM %s LIMIT 5' % table
        self.cur.execute(order)
        rows = self.cur.fetchall()
        self.closeMysql()
        ips = []
        for row in rows:
            ip = row[1] + ':' + row[2]
            ips.append(ip)
        return ips

    def closeMysql(self):
        self.cur.close()
        self.conn.close()


if __name__ == "__main__":
    mysql = mySql()
    ips = mysql.selectIpPort('webIp')
    print(ips)
