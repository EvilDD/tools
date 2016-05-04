import requests
from bs4 import BeautifulSoup
from random import choice
from urllib.parse import urlparse, unquote
from noUrl import noUrls
import re
from time import sleep


class baseSearch(object):
    """搜索引擎基类"""

    def __init__(self, keywords):
        self.keywords = keywords  # 搜索引擎关键字
        self.waitTime = 5  # 设置超时
        self.agent = [
            'Mozilla/5.0 (Linux i686; U; en; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 10.51',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.7; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.0 Safari/534.24',
            'Mozilla/5.0 (Linux; U; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13'
        ]
        self.getPageUrl()  # 子类中实现

    def getPageHtml(self, url, payload):  # 获取第n页的源码
        headers = {
            'User-Agent': choice(self.agent)
        }
        req = requests.get(url, params=payload, headers=headers, timeout=self.waitTime)
        req.encoding = 'utf-8'
        return req.text

    def saveUrls(self, urls, name=None):  # 按浏览器名字分类保存主域名
        if name is None:  # 代表合并存储
            with open('allUrls.txt', 'a', encoding='utf-8') as f:
                f.writelines(urls)
        else:  # 分开存储
            txt = name + '.txt'
            with open(txt, 'a', encoding='utf-8') as f:
                f.writelines(urls)

    def delRepUrls(self, filePath):  # 去除重复和比兑不需要检测的url
        with open(filePath, 'r', encoding='utf-8') as f:
            urls = f.readlines()
        firstUrl = urls[0]
        if '\ufeff' in firstUrl:  # 如果文本是utf-8会出现这样字符
            urls[0] = urls[0].strip('\ufeff')
        lastUrl = urls[len(urls) - 1]
        if '\n' not in lastUrl:  # 避免最后一个没有回车重复
            urls[len(urls) - 1] += '\n'
        tempUrls = set(urls).difference(set(noUrls))  # 取与noUrls中不存在的元素
        newUrls = list(tempUrls)
        with open(filePath, 'w', encoding='utf-8') as f:
            f.writelines(newUrls)


class biyingSearch(baseSearch):
    """必应搜索引擎"""

    def handleHtml(self, html):  # 处理html中的url
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

    def getPageUrl(self):
        fileName = '必应'
        url = 'http://cn.bing.com/search'
        for i in range(100):  # 不可能有一百页直到采集结束
            try:
                payload = {'q': self.keywords, 'first': i * 10}
                html = self.getPageHtml(url, payload)
                if '<div class="sw_next">下一页' in html:
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                else:  # 这里进行最后一页采集再跳出
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                    print('==========最后一页采集完毕===========')
                    f = fileName + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls(fileName + '.txt')


class sosoSearch(baseSearch):
    """360搜索引擎"""

    def handleHtml(self, html):  # 处理html中的url
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

    def getPageUrl(self):  # 获取第所有页数以及处理获取urls写入文件
        fileName = '奇虎'
        url = 'http://www.so.com/s'
        for i in range(100):
            try:
                payload = {'q': self.keywords, 'pn': i + 1}
                html = self.getPageHtml(url, payload)
                if '下一页</a>' in html:
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                else:  # 这里进行最后一页采集再跳出
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                    print('==========最后一页采集完毕===========')
                    f = fileName + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls(fileName + '.txt')


class baiduSearch(baseSearch):
    """百度搜索引擎"""

    def targetUrl(self, url):
        try:
            r = requests.get(url, allow_redirects=False, timeout=self.waitTime)  # 不跳转
            if r.status_code == 200:
                return r.url
            elif r.status_code == 302:
                return r.headers.get('location')  # 这就是大牛高效的思想
        except:
            # print('丢弃超时网址!')
            pass

    def handleHtml(self, html):  # 不同浏览器不一样,可重写方法
        soup = BeautifulSoup(html, 'lxml')
        comtent = soup.find_all(id='content_left')  # 找到目标div大模块
        rule = re.compile('href="(.*?)"')
        links = re.findall(rule, repr(comtent))
        links = list(set(links))  # 去重一次
        urls = []  # 过滤上面url获取主域名
        for url in links:
            if url.startswith('http://www.baidu.com/link?url='):  # 精确目标网址
                url = self.targetUrl(url)  # 百度外链返回真正的url
                if url is not None:  # 剔出无法访问的url
                    parse = urlparse(url)
                    url = parse.scheme + '://' + parse.netloc + '\n'
                    urls.append(url)
        return urls

    def getPageUrl(self):
        fileName = '百度'
        url = 'http://www.baidu.com/s'
        for i in range(100):
            try:
                payload = {'wd': self.keywords, 'pn': i * 10}
                html = self.getPageHtml(url, payload)
                if '下一页&gt;</a></div><div id="content_bottom">' in html:  # 防止死循环,百度访问不存在的末页会跳转第一页
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                else:  # 这里进行最后一页采集再跳出
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                    print('==========最后一页采集完毕===========')
                    f = fileName + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls(fileName + '.txt')


class sogouSearch(baseSearch):
    """搜狗搜索引擎"""

    def targetUrl(self, url):
        try:
            r = requests.get(url, allow_redirects=False, timeout=self.waitTime)  # 不跳转
            if r.status_code == 200:
                rule = 'window.location.replace\("(.*?)"'
                url = re.findall(rule, r.text)
                if url != []:
                    return url[0]
            else:  # 搜狗策略不同
                print('不同的状态码', r.status_code)
        except:
            # print('丢弃超时网址!')
            pass

    def handleHtml(self, html):  # 不同浏览器不一样,可重写方法
        soup = BeautifulSoup(html, 'lxml')
        comtent = soup.find_all(class_='results')  # 找到目标div大模块
        rule = re.compile('href="(.*?)"')
        links = re.findall(rule, repr(comtent))
        links = list(set(links))  # 去重一次
        urls = []  # 过滤上面url获取主域名
        for url in links:
            if url.startswith('http://www.sogou.com/link?url='):  # 精确目标网址
                url = self.targetUrl(url)  # 百度外链返回真正的url
                if url is not None:  # 剔出无法访问的url
                    parse = urlparse(url)
                    url = parse.scheme + '://' + parse.netloc + '\n'
                    urls.append(url)
        return urls

    def getPageUrl(self):  # 获取第所有页数以及处理获取urls写入文件
        fileName = '搜狗'
        url = 'https://www.sogou.com/web'
        for i in range(100):
            try:
                payload = {'query': self.keywords, 'page': i + 1}
                html = self.getPageHtml(url, payload)
                if '下一页</a> <div class="mun">' in html or '下一页 ></a> <div class="mun">' in html:
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                else:  # 这里进行最后一页采集再跳出
                    urls = self.handleHtml(html)
                    print('%s第%d页采集' % (fileName, (i + 1)))
                    self.saveUrls(urls, name=fileName)
                    print('==========最后一页采集完毕===========')
                    f = fileName + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls(fileName + '.txt')
if __name__ == '__main__':
    # a = biyingSearch('inurl:install/index.php')
    # b = sosoSearch('inurl:install/index.php')
    c = sogouSearch('inurl:install/index.php')
    # d = baiduSearch('inurl:install/index.php')
