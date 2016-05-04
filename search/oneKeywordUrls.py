#!/usr/bin/python3
# from crawlerData import mySql
import requests
import queue
import threading
from random import choice
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote
import pymysql
import re

keywords = input('请输入搜索关键字:')
thread_num = 100  # 线程数
page_num = 100  # 页数
urlQL = threading.Lock()
urlQ = queue.Queue()
threads = []
exitFlag = 0

byHtmls = []  # 必应提取的html
qhHtmls = []  # 奇虎360提取的html
bdHtmls = []  # 百度提取的html

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
        order = 'SELECT * FROM useIp ORDER BY timeout LIMIT 200'
        cur.execute(order)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for row in rows:
            ipProxys.append(row[1])
        if ipProxys == []:  # 未获取到代理ip就继续获取
            getIpProxy()
        print('已获取代理ip')
    except Exception as e:
        print('获取代理ip失败', e)
    return ipProxys

ipiter = getIpProxy()  # 200代理ip列表


class myThread(threading.Thread):

    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        # print("开启线程：" + self.name)
        self.getHtmls()
        # print("退出线程：" + self.name)

    def getHtmls(self):
        while not exitFlag:
            urlQL.acquire()
            if not urlQ.empty():
                url = self.q.get()  # 获取一个url
                urlQL.release()
                # print("%s processing %s" % (self.name, url))
                self.getPage(url)
            else:
                urlQL.release()

    def getPage(self, url):
        headers = {'User-Agent': choice(agent)}
        try:
            rep = requests.get(url, headers=headers)  # 考虑验证码和代理
            rep.encoding = 'utf-8'
            if 'cn.bing.com' in url:
                byHtmls.append(rep.text)
            elif 'www.so.com' in url:
                qhHtmls.append(rep.text)
            elif 'www.baidu.com' in url:
                if 'http://verify.baidu.com/verify' in rep.text:  # 需要验证码
                    while True:  # 一直请求直到代理ip可以获取不需要验证码的页面
                        ip = choice(ipiter)
                        proxies = {'http': 'http://%s' % ip}
                        print('百度正在使用代理ip:%s' % ip)
                        try:
                            rep = requests.get(url, headers=headers, proxies=proxies)
                            rep.encoding = 'utf-8'
                            if 'http://verify.baidu.com/verify' in rep.text:  # 若代理ip也需要验证码继续
                                pass
                            else:  # 代理ip获取页面不需要验证码退出并加入html列表
                                bdHtmls.append(rep.text)
                                break
                        except:
                            print('代理ip访问失败,切换代理!')
                else:
                    bdHtmls.append(rep.text)
            else:
                print('竟然会没有url???')
        except:
            print('%s超时获取失败,再次进行获取' % url)


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
    urlQL.release()
    while not urlQ.empty():
        pass
    exitFlag = 1
    for t in threads:
        t.join()
    print('必应%d页,奇虎%d页,百度%d页' % (len(byHtmls), len(qhHtmls), len(bdHtmls)))


def byhandleHtml(html):  # 处理必应html中的url
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all(target="_blank")  # 找到这个标签所有目标链接
    urls = []  # 处理过的url
    for link in links:
        url = link.get('href')
        parse = urlparse(url)
        url = parse.scheme + '://' + parse.netloc + '\n'
        urls.append(url)
    urls = list(set(urls))  # 去重
    return urls


def qhhandleHtml(html):  # 处理奇虎html中的url
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all('a')
    urls = []
    for link in links:
        if link.get('data-res') is not None:  # 找目标链接
            url = link.get('href')
            if url is not None:  # 去掉为None的元素
                rule = re.compile('url=(.*?)&q')
                try:  # 360有时候是直接显示目标网址
                    url = re.findall(rule, url)[0]
                    url = unquote(url)
                except:
                    pass
                parse = urlparse(url)
                url = parse.scheme + '://' + parse.netloc + '\n'
                urls.append(url)
    urls = list(set(urls))  # 初步去重复
    return urls


def targetUrl(url):  # 百度
    try:
        r = requests.get(url, allow_redirects=False)  # 不跳转
        if r.status_code == 200:
            return r.url
        elif r.status_code == 302:
            return r.headers.get('location')  # 这就是大牛高效的思想
    except:
        # print('丢弃超时网址!')
        pass


def bdhandleHtml(html):  # 处理百度html
    soup = BeautifulSoup(html, 'lxml')
    comtent = soup.find_all(id='content_left')  # 找到目标div大模块
    rule = re.compile('href="(.*?)"')
    links = re.findall(rule, repr(comtent))
    links = list(set(links))  # 去重一次
    urls = []  # 过滤上面url获取主域名
    for url in links:
        if url.startswith('http://www.baidu.com/link?url='):  # 精确目标网址
            url = targetUrl(url)  # 百度外链返回真正的url
            if url is not None:  # 剔出无法访问的url
                parse = urlparse(url)
                url = parse.scheme + '://' + parse.netloc + '\n'
                urls.append(url)
    return urls


def saveUrls(urls, name=None):  # 按浏览器名字分类保存主域名
    if name is None:  # 代表合并存储
        with open('oneKeyUrls.txt', 'a', encoding='utf-8') as f:
            f.writelines(urls)
    else:  # 分开存储
        txt = name + '.txt'
        with open(txt, 'a', encoding='utf-8') as f:
            f.writelines(urls)


def delRepUrls(filePath):  # 去除重复和比兑不需要检测的url
    with open(filePath, 'r', encoding='utf-8') as f:
        urls = f.readlines()
    firstUrl = urls[0]
    if '\ufeff' in firstUrl:  # 如果文本是utf-8会出现这样字符
        urls[0] = urls[0].strip('\ufeff')
    lastUrl = urls[len(urls) - 1]
    if '\n' not in lastUrl:  # 避免最后一个没有回车重复
        urls[len(urls) - 1] += '\n'
    # tempUrls = set(urls).difference(set(noUrls))  # 取与noUrls中不存在的元素
    newUrls = list(set(urls))
    with open(filePath, 'w', encoding='utf-8') as f:
        f.writelines(newUrls)

baiduQ = queue.Queue()
baiduQL = threading.Lock()
bdExit = 0
thds = []


class bdThread(threading.Thread):

    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q

    def run(self):
        # print('开线程:' + self.name)
        while not bdExit:
            baiduQL.acquire()
            if not baiduQ.empty():
                html = self.q.get()
                baiduQL.release()
                # print("%s processing %s" % (self.name, '第nhtml'))
                bdurls = bdhandleHtml(html)
                saveUrls(bdurls)
            else:
                baiduQL.release()
        # print('关线程:' + self.name)


def main():
    getSearchHtmls()
    print('获取html页面成功,准备提取正确url')
    for h in byHtmls:
        byurls = byhandleHtml(h)
        saveUrls(byurls)
    print('必应采集完毕')
    for h in qhHtmls:
        qhurls = qhhandleHtml(h)
        saveUrls(qhurls)
    print('奇虎采集完毕')
    global bdExit
    for t in range(thread_num):
        tName = "Thread-%d" % (t + 1)
        thd = bdThread(tName, baiduQ)
        thd.start()
        thds.append(thd)
    baiduQL.acquire()
    for h in bdHtmls:
        baiduQ.put(h)
    baiduQL.release()
    while not baiduQ.empty():
        pass
    bdExit = 1
    for t in thds:
        t.join()
    print('百度采集完毕')
    delRepUrls('oneKeyUrls.txt')
    print('<======去重结束,采集完毕======>')

if __name__ == '__main__':
    main()
