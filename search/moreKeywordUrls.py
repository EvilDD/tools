import requests
import queue
import threading
from random import choice
from bs4 import BeautifulSoup
import time

proNum = 1  # 进度
thread_num = 10  # 线程数
urlQL = threading.Lock()
urlQ = queue.Queue()
threads = []
exitFlag = 0

# byHtmls = []  # 必应提取的html

agent = [
    'Mozilla/5.0 (Linux i686; U; en; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 10.51',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.7; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.0 Safari/534.24',
    'Mozilla/5.0 (Linux; U; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13'
]


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
        global proNum
        headers = {'User-Agent': choice(agent)}
        try:
            rep = requests.get(url, headers=headers)
            rep.encoding = 'utf-8'
            # byHtmls.append(rep.text)
            byhandleHtml(rep.text)
            print("正在处理第%d个页面" % proNum)
            proNum += 1
        except:
            print('由于网络原因第%d个页面%s处理失败' % (proNum, url))
            proNum += 1


def getSearchHtmls():
    global exitFlag
    for i in range(thread_num):
        tName = 'Thread-%d' % (i + 1)
        thread = myThread(tName, urlQ)
        thread.start()
        threads.append(thread)
    urlQL.acquire()  # 填充队列
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = f.readlines()
    for keyword in keywords:
        keyword = keyword.strip()
        url = 'http://cn.bing.com/search?q=%s&first=1' % keyword  # 必应url
        urlQ.put(url)
    urlQL.release()
    while not urlQ.empty():
        pass
    exitFlag = 1
    for t in threads:
        t.join()
    # print('已成功获取%d个关键词页面' % (len(byHtmls)))


def byhandleHtml(html):  # 处理必应html中的url并保存
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all(target="_blank")  # 找到这个标签所有目标链接
    urls = []  # 处理过的url
    for link in links:
        url = link.get('href')
        # parse = urlparse(url)
        # url = parse.scheme + '://' + parse.netloc + '\n'
        url = url + '\n'
        urls.append(url)
    urls = list(set(urls))  # 列表去重
    with open('moreKeyUrls.txt', 'a', encoding='utf-8') as f:
        f.writelines(urls)
    delRepUrls('moreKeyUrls.txt')  # 文本再去重


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


def main():
    print("<======采集开始======>")
    print(time.ctime())
    start = time.time()
    getSearchHtmls()
    # print('获取html页面成功,准备提取正确url')
    # for html in byHtmls:
    #     byhandleHtml(html)
    print(time.ctime())
    print("耗时%f秒" % (time.time() - start))
    print('<======采集完毕======>')
if __name__ == '__main__':
    main()
