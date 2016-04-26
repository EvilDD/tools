import requests
from bs4 import BeautifulSoup
from random import choice
from urllib.parse import urlparse, unquote
from noUrl import noUrls
import re


class baseSearch(object):
    """搜索引擎基类"""

    def __init__(self, keywords, outOriUrl=False):  # outoriurl 控制是否输出原始带路径的url
        self.keywords = keywords  # 搜索引擎关键字
        self.waitTime = 5  # 设置超时
        self.agent = [
            'Mozilla/5.0 (Linux i686; U; en; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 Opera 10.51',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.7; en-US; rv:1.9.2.2) Gecko/20100316 Firefox/3.6.2',
            'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.0 Safari/534.24',
            'Mozilla/5.0 (Linux; U; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13'
        ]
        self.getPageUrl(outOriUrl)

    def getPageHtml(self, url, payload):  # 获取第n页的源码
        headers = {
            'User-Agent': choice(self.agent)
        }
        req = requests.get(url, params=payload, headers=headers, timeout=self.waitTime)
        # print(req.url, req.encoding)
        req.encoding = 'utf-8'
        return req.text

    def saveUrls(self, originUrls, urls, outOriUrl, name=None):  # 按浏览器名字分类保存,原始url和主域名
        if name is None:  # 代表合并存储
            with open('allUrls.txt', 'a', encoding='utf-8') as f:
                f.writelines(urls)
            if outOriUrl:
                with open('originAllUrls.txt', 'a', encoding='utf-8') as f:
                    f.writelines(originUrls)
        else:  # 分开存储
            txt = '主域名' + name + '.txt'
            with open(txt, 'a', encoding='utf-8') as f:
                f.writelines(urls)
            if outOriUrl:
                txt = '原始' + name + '.txt'
                with open(txt, 'a', encoding='utf-8') as f:
                    f.writelines(originUrls)

    def delRepUrls(self, filePath):  # 去除重复和比况不需要检测的url
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

    def defRepPathUrls(self, filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            originUrls = f.readlines()
            netlocs = []  # 主机域名
            targetUrls = []  # 保留一个主域名一样的完整url
            for url in originUrls:
                parse = urlparse(url)
                if parse.netloc not in netlocs:
                    netlocs.append(parse.netloc)  # 添加,下次不出现相同域名
                    targetUrls.append(url)
        with open(filePath, 'w', encoding='utf-8') as f:
            f.writelines(targetUrls)


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
        url = 'http://cn.bing.com/search'
        for i in range(100):  # 不可能有一百页直到采集结束
            try:
                payload = {'q': self.keywords, 'first': i * 10}
                html = self.getPageHtml(url, payload)
                if '<div class="sw_next">下一页' in html:
                    urls = self.handleHtml(html)
                    print('必应第%d页采集' % (i + 1))
                    self.saveUrls(urls, name='by')
                else:  # 这里进行最后一页采集再跳出
                    urls = self.handleHtml(html)
                    print('必应第%d页采集' % (i + 1))
                    self.saveUrls(urls, name='by')
                    print('==========最后一页采集完毕===========')
                    f = 'html/by' + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls('by.txt')


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
        url = 'http://www.so.com/s'
        for i in range(100):
            try:
                payload = {'q': self.keywords, 'pn': i + 1}
                html = self.getPageHtml(url, payload)
                if '下一页</a>' in html:
                    urls = self.handleHtml(html)
                    print('360搜搜第%d页采集' % (i + 1))
                    self.saveUrls(urls, name='360')
                else:  # 这里进行最后一页采集再跳出
                    urls = self.handleHtml(html)
                    print('360搜搜第%d页采集' % (i + 1))
                    self.saveUrls(urls, name='360')
                    print('==========最后一页采集完毕===========')
                    f = 'html/ss' + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls('360.txt')


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
        originUrls = []  # 原始完整url
        urls = []  # 过滤上面url获取主域名
        for url in links:
            if url.startswith('http://www.baidu.com/link?url='):  # 精确目标网址
                url = self.targetUrl(url)  # 百度外链返回真正的url
                if url is not None:  # 剔出无法访问的url
                    originUrl = url + '\n'
                    originUrls.append(originUrl)
                    parse = urlparse(url)
                    url = parse.scheme + '://' + parse.netloc + '\n'
                    urls.append(url)
        return originUrls, urls

    def getPageUrl(self, outOriUrl):
        url = 'http://www.baidu.com/s'
        for i in range(100):
            try:
                payload = {'wd': self.keywords, 'pn': i * 10}
                html = self.getPageHtml(url, payload)
                if '下一页&gt;</a></div><div id="content_bottom">' in html:  # 防止死循环,百度访问不存在的末页会跳转第一页
                    originUrls, urls = self.handleHtml(html)
                    print('百度第%d页采集' % (i + 1))
                    self.saveUrls(originUrls, urls, outOriUrl, name='bd')
                else:  # 这里进行最后一页采集再跳出
                    originUrls, urls = self.handleHtml(html)
                    print('百度第%d页采集' % (i + 1))
                    self.saveUrls(originUrls, urls, outOriUrl, name='bd')
                    print('==========最后一页采集完毕===========')
                    f = 'html/bd' + repr(i + 1) + '.html'
                    with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
                        f.write(html)
                    break
            except:
                print("您当前网络不好,远程计算机拒绝连接!")
        self.delRepUrls('主域名bd.txt')
        if outOriUrl:  # 输出即去下重复的主域名
            self.defRepPathUrls('原始bd.txt')
if __name__ == '__main__':
    # a = biyingSearch('inurl:install/index.php')
    # a.getPageUrl()
    # b = sosoSearch('inurl:install/index.php')
    # b.getPageUrl()
    c = sosoSearch('inurl:install/index.php')
    # c.getPageUrl()
    # d = baiduSearch("inurl:install/index.php", outOriUrl=True)


# class sogouSearch(baseSearch):
#     """搜狗搜索引擎"""

#     def handleHtml(self, html):
#         soup = BeautifulSoup(html, 'lxml')
#         links = soup.find_all('cite')
#         urls = []
#         for link in links:
#             url = link.string
#             if url is not None:  # 去掉为None的元素
#                 url = 'http://' + url
#                 parse = urlparse(url)
#                 url = parse.scheme + '://' + parse.netloc + '\n'
#                 urls.append(url)
#         urls = list(set(urls))  # 去重
#         return urls

#     def getPageUrl(self):  # 获取第所有页数以及处理获取urls写入文件
#         url = 'https://www.sogou.com/web'
#         for i in range(100):
#             try:
#                 payload = {'query': self.keywords, 'page': i + 1}
#                 html = self.getPageHtml(url, payload)
#                 if '下一页' in html:
#                     urls = self.handleHtml(html)
#                     print('搜狗第%d页采集' % (i + 1))
#                     self.saveUrls(urls, name='sg')
#                 else:  # 这里进行最后一页采集再跳出
#                     urls = self.handleHtml(html)
#                     print('搜狗第%d页采集' % (i + 1))
#                     self.saveUrls(urls, name='sg')
#                     print('==========最后一页采集完毕===========')
#                     f = 'html/sg' + repr(i + 1) + '.html'
#                     with open(f, 'w', encoding='utf-8') as f:  # 打印跳出时界面
#                         f.write(html)
#                     break
#             except:
#                 print("您当前网络不好,远程计算机拒绝连接!")
#         self.delRepUrls('sg.txt')
