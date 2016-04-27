#!/usr/bin/python3
from crawlerData import mySql
import requests
import queue
import threading
from time import time

thread_num = 10
ipQueueLock = threading.Lock()
ipQueue = queue.Queue()
threads = []
timeout = 5  # 设置延时
validIp = []  # 过滤出的有效ip
exitFlag = 0


class myThread (threading.Thread):

    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        print("开启线程：" + self.name)
        self.getIp(self.name, self.q)
        print("退出线程：" + self.name)

    def getIp(self, threadName, q):
        while not exitFlag:
            ipQueueLock.acquire()
            if not ipQueue.empty():
                ip = q.get()
                ipQueueLock.release()
                print("%s processing %s" % (threadName, ip))
                self.verifyIp(ip)  # 因为第一次queue是空的,所以获取不到ip,放到if中执行
            else:
                ipQueueLock.release()

    def verifyIp(self, ip):  # 获取队列值并验证ip是否有效
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
            print(end - start)
            r.encoding = 'utf-8'
            if '京ICP证030173号' in r.text:
                validIp.append(ip)
            else:
                print('无效ip:%s' % ip)
        except:
            print('延时ip:%s' % ip)


def ipList():
    ips = []
    mysql = mySql()
    ipList1 = mysql.selectIpPort('webIp')
    ips = ipList1
    if ips == []:
        print('获取数据ip失败!')
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
    # while not ipQueue.empty():  # 等待队列清空
    #     队列空了,dosomethin
    exitFlag = 1    # 通知线程是时候退出
    for t in threads:    # 等待所有线程完成
        t.join()
    print("退出主线程", len(validIp))
if __name__ == '__main__':
    main()
