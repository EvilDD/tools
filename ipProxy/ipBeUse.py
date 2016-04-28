#!/usr/bin/python3
from crawlerData import mySql
import requests
import queue
import threading
from time import time, sleep, ctime

thread_num = 100
ipQueueLock = threading.Lock()
ipQueue = queue.Queue()
threads = []
timeout = 5  # 设置延时
validIps = []  # 过滤出的有效ip
exitFlag = 0
noValidIps = []  # 超时和无效的ip


class myThread (threading.Thread):

    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        # print("开启线程：" + self.name)
        self.getIp(self.name, self.q)
        # print("退出线程：" + self.name)

    def getIp(self, threadName, q):
        while not exitFlag:
            ipQueueLock.acquire()
            if not ipQueue.empty():
                ip = q.get()
                ipQueueLock.release()
                # print("%s processing %s" % (threadName, ip))
                self.verifyIp(ip)  # 因为第一次queue是空的,所以获取不到ip,放到if中执行
            else:
                ipQueueLock.release()

    def verifyIp(self, ip):  # 获取队列值并验证ip是否有效
        ipTime = []  # 装ip和访问时间
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        proxies = {
            "http": ip,
        }
        try:
            start = time()
            r = requests.get('http://www.baidu.com', headers=headers, proxies=proxies, timeout=timeout)
            end = time()
            time_out = end - start
            ipTime.append(ip)
            ipTime.append(time_out)
            r.encoding = 'utf-8'
            if '京ICP证030173号' in r.text:
                validIps.append(ipTime)
            else:
                noValidIps.append(ip)
                # print('无效ip:%s' % ip)
                pass
        except:
            noValidIps.append(ip)
            # print('延时ip:%s' % ip)
            pass


def ipList():
    ips = []
    mysql = mySql()
    ipList1 = mysql.selectIpPort('webIp')
    conectWebIp = True
    while conectWebIp:
        if ipList1 == []:
            print('获取webIp数据失败!%s' % (ctime()))
            sleep(3)
            mysql = mySql()
            ipList1 = mysql.selectIpPort('webIp')  # 获取失败再获取一次
        else:
            conectWebIp = False
    ips = ipList1
    return ips


def main():
    global exitFlag
    for tName in range(thread_num):  # 创建新线程
        tName = "Thread-%d" % (tName + 1)
        thread = myThread(tName, ipQueue)
        thread.start()
        threads.append(thread)
    ips = ipList()  # ip列表
    ipQueueLock.acquire()  # 填充队列
    for ip in ips:
        ipQueue.put(ip)
    ipQueueLock.release()
    while not ipQueue.empty():  # 等待队列清空
        pass
    exitFlag = 1    # 通知线程是时候退出
    for t in threads:    # 等待所有线程完成
        t.join()
    mysql = mySql()
    print("退出主线程,此次可用ip%d,过滤ip%d" % (len(validIps), len(noValidIps)))
    mysql.clearTable('useIp')
    mysql.insertUseIp(validIps)

if __name__ == '__main__':
    main()
