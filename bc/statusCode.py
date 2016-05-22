#!/usr/bin/python3

import requests
import queue
import threading

exitFlag = 0
proNum = 1


class myThread (threading.Thread):

    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        # print("开启线程：" + self.name)
        process_data(self.name, self.q)
        # print("退出线程：" + self.name)


def saveUrl(url, name):
    url += '\n'
    name = repr(name)
    name += '.txt'
    with open(name, 'a', encoding='utf-8') as f:
        f.write(url)


def process_data(threadName, q):
    global proNum
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            try:
                rep = requests.get(data, timeout=5)
                code = rep.status_code
                saveUrl(data, code)
                if proNum % 100 == 0:
                    print("已完成%d个url筛选" % proNum)
                proNum += 1
            except:
                proNum += 1
                pass
            # print("%s processing %s" % (threadName, data))
        else:
            queueLock.release()


threadList = 300
queueLock = threading.Lock()
workQueue = queue.Queue()
threads = []
threadID = 1

# 创建新线程
for tName in range(threadList):
    thread = myThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# 填充队列
with open('1.txt', 'r', encoding='utf-8') as f:
    urls = f.readlines()
queueLock.acquire()
for url in urls:
    url = url.strip().strip('\ufeff')
    workQueue.put(url)
queueLock.release()

# 等待队列清空
while not workQueue.empty():
    pass

# 通知线程是时候退出
exitFlag = 1

# 等待所有线程完成
for t in threads:
    t.join()
print("退出主线程")
