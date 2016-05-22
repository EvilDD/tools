#!/usr/bin/python3
import queue
import threading
from selenium import webdriver
import re
from urllib.parse import urlparse

exitFlag = 0
proNum = 1


class myThread (threading.Thread):

    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        print("开启线程：" + self.name)
        process_data(self.name, self.q)
        print("退出线程：" + self.name)


def getHtml(url):
    drvier = webdriver.PhantomJS()
    drvier.get(url)
    html = drvier.page_source
    drvier.quit()
    return html


def getUrl(html):
    rule = re.compile('"(http://.*?)"')
    urls = re.findall(rule, html)
    newUrls = []
    for url in urls:
        parse = urlparse(url)
        pattern = re.compile(r'\d+')
        nums = pattern.search(parse.netloc)
        if nums is not None:  # url中带数字的再获取主域名
            url = parse.scheme + '://' + parse.netloc + '\n'
            newUrls.append(url)
    newUrls = list(set(newUrls))
    return newUrls


def process_data(threadName, q):
    global proNum
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            try:
                html = getHtml(data)
                urls = getUrl(html)
                with open('bcUrls.txt', 'a', encoding='utf-8') as f:
                    f.writelines(urls)
                if proNum % 100 == 0:
                    print('===================================完成%d个url处理' % proNum)
                proNum += 1
            except Exception as e:
                print(e)
                proNum += 1
                pass
            print("%s processing %s" % (threadName, data))
        else:
            queueLock.release()


threadList = 10
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
with open('200.txt', 'r', encoding='utf-8') as f:
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
