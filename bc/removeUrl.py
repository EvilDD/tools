from urllib.parse import urlparse
f1 = input("输入过滤文件名:")
with open(f1, 'r', encoding='utf-8') as f:
    urls = f.readlines()
newUrls = []
for url in urls:
    if 'http://' not in url:
        pass
    elif 'www.yzyouth.com' in url:
        pass
    elif 'www.aizhan.com' in url:
        pass
    elif 'www.guochengfp.net' in url:
        pass
    elif '.taobao.com' in url:
        pass
    elif '.baidu.com' in url:
        pass
    elif 'www.52suda.com' in url:
        pass
    elif '.sogou.com' in url:
        pass
    elif 'www.58.com' in url:
        pass
    elif 'www.iqiyi.com' in url:
        pass
    elif '.qq.com' in url:
        pass
    elif '.sina.com' in url:
        pass
    elif '.weibo.com' in url:
        pass
    else:
        newUrls.append(url)
newUrls.sort()  # 列表正序排序
depUrls = []
tmpUrls = []
for url in newUrls:  # 同一域名只取第一个url
    parse = urlparse(url)
    if parse.netloc not in depUrls:
        depUrls.append(parse.netloc)
        tmpUrls.append(url)
f1 = "new" + f1
with open(f1, 'w', encoding='utf-8') as f:
    f.writelines(tmpUrls)
