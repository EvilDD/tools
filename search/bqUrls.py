#!/usr/bin/python3
# from crawlerData import mySql
import requests
import queue
import threading
from time import time, sleep, ctime
from random import choice
import pymysql

keywords = 'inurl:install/index.php'
thread_num = 10  # 线程数
page_num = 10  # 页数
urlQL = threading.Lock()
urlQ = queue.Queue()
threads = []
exitFlag = 0

byHtmls = []  # 必应提取的html
qhHtmls = []  # 奇虎360提取的html
bdHtmls = []  # 百度提取的html
sgHtmls = []  # 搜狗提取的html

timeout = 5  # 设置延时
agent = [
    'Mozilla/5.0 (Linux i686; U; en; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 10.51',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.7; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.0 Safari/534.24',
    'Mozilla/5.0 (Linux; U; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13'
]


def getIpProxy():  # 获取远程此时可用代理ip
    ipProxys = []  # 代理ip列表
    try:
        conn = pymysql.connect(
            database='crawler',
            user='root',
            password='dong.56100',
            host='104.224.140.213',  # localhost
            port=3306
        )
        cur = conn.cursor()
        order = 'SELECT * FROM useIp ORDER BY timeout'
        cur.execute(order)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for row in rows:
            ipProxys.append(row[1])
        if ipProxys == []:  # 未获取到代理ip就继续获取
            getIpProxy()
        print('已获取代理ip')
        ipiter = iter(ipProxys)
    except Exception as e:
        print('获取代理ip失败', e)
    return ipiter

ipiter = getIpProxy()  # 代理ip迭代器


class myThread(threading.Thread):

    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        print("开启线程：" + self.name)
        self.getHtmls()
        print("退出线程：" + self.name)

    def getHtmls(self):
        while not exitFlag:
            url = self.q.get()  # 获取一个url
            print("%s processing %s" % (self.name, url))
            headers = {'User-Agent': choice(agent)}
            rep = requests.get(url, headers=headers)  # 考虑验证码和代理
            rep.encoding = 'utf-8'
            if 'cn.bing.com' in url:
                byHtmls.append(rep.text)
            elif 'www.so.com' in url:
                qhHtmls.append(rep.text)
            elif 'www.baidu.com' in url:
                bdHtmls.append(rep.text)
            elif 'www.sogou.com' in url:
                if 'alt="请输入图中的验证码" title="请输入图中的验证码"' in rep.text:
                    while True:
                        try:
                            proxies = {'http': 'http://%s' % (next(ipiter))}
                            print(proxies)
                            rep = requests.get(url, headers=headers, proxies=proxies)
                            if 'alt="请输入图中的验证码" title="请输入图中的验证码"' not in rep.text:
                                break
                            sgHtmls.append(rep.text)
                        except Exception as e:
                            print('代理ip!', proxies, e)
                            break
                else:
                    sgHtmls.append(rep.text)
            else:
                print('竟然会没有url???')


def getSearchHtmls():
    global exitFlag
    for i in range(thread_num):
        tName = 'Thread-%d' % (i + 1)
        thread = myThread(tName, urlQ)
        thread.start()
        threads.append(thread)
    urlQL.acquire()  # 填充队列
    for i in range(page_num):
        url = 'http://cn.bing.com/search?q=%s&first=%d' % (keywords, i * 10)  # 必应url
        urlQ.put(url)
        url = 'http://www.so.com/s?q=%s&pn=%d' % (keywords, i + 1)  # 奇虎url
        urlQ.put(url)
        url = 'http://www.baidu.com/s?wd=%s&pn=%d' % (keywords, i * 10)  # 百度url
        urlQ.put(url)
        url = 'https://www.sogou.com/web?query=%s&page=%d' % (keywords, i + 1)  # 搜狗url
        urlQ.put(url)
    urlQL.release()
    while not urlQ.empty():
        pass
    exitFlag = 1
    for t in threads:
        t.join()
    print('必应%d,奇虎%d,百度%d,搜狗%d' % (len(byHtmls), len(qhHtmls), len(bdHtmls), len(sgHtmls)))
    for i in range(len(byHtmls)):
        byfile = 'by/%d.html' % (i + 1)
        with open(byfile, 'w', encoding='utf-8') as f:
            f.write(byHtmls[i])
    for i in range(len(qhHtmls)):
        qhfile = 'qh/%d.html' % (i + 1)
        with open(qhfile, 'w', encoding='utf-8') as f:
            f.write(qhHtmls[i])
    for i in range(len(bdHtmls)):
        bdfile = 'bd/%d.html' % (i + 1)
        with open(bdfile, 'w', encoding='utf-8') as f:
            f.write(bdHtmls[i])
    for i in range(len(sgHtmls)):
        sgfile = 'sg/%d.html' % (i + 1)
        with open(sgfile, 'w', encoding='utf-8') as f:
            f.write(sgHtmls[i])

if __name__ == '__main__':
    getSearchHtmls()
