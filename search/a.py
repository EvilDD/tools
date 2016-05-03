import re
from urllib.request import urlopen
import time
import threading
# 进程锁
lock = threading.Lock()
# 存放记录条数
count = 0
# 存放url信息
url = []


# 第一次正则匹配搜索结果
rc = re.compile(r'(<span class="g">)(.*)[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}', re.I)

# 第二次正则匹配搜索结果
rcr = re.compile(r'^>(.*)(/&nbsp;)?(\s)?', re.I)
# 替换重复的搜索结果
# 多线程搜索


class SeoRearch(threading.Thread):

    def __init__(self, wd='dedecms', n=0):
        self.wd = wd
        self.n = n
        super(SeoRearch, self).__init__()

    def run(self):
        global count
        file = urlopen("http://www.baidu.com/s?rn=50&pn=" + str(self.n) + "&q1=" + self.wd).read()
        for i in rc.finditer(file):
            f = i.group(0)
            temp = f.replace('<b>', '').replace('</b>', '')
            time.sleep(1)
            t = temp[16:temp.find('/')]
            print(t)
            lock.acquire()
            url.append(t)
            count += 1
            lock.release()
if __name__ == '__main__':
    s = input("请输入你要查询的关键字")
    Page = input("请输入要查询的页数每页50条")
    file1 = open('record.txt', 'w')
    threads = []
    for i in range(int(Page)):
        t = SeoRearch(wd=s, n=i * 50)
        t.start()
        threads.append(t)

    for t2 in threads:
        t2.join()

    list_insteah = list(set(url))
    time.sleep(2)
    for i in list_insteah:
        file1.write(i + "\n")

    file1.close()
    print("你搜索的关键字是:%s,搜索的页数是:%s,总计一共 %s 条信息" % (s, Page, count))
