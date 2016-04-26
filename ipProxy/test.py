#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
proxies = {
    "http": "111.161.126.107:80",
}
a = time.time()
try:
    r = requests.get('http://httpbin.org/ip', proxies=proxies)
    b = time.time()
    if '117.21.182.110' in r.text:
        print(b - a)
    else:
        print(r.text)
        print(b - a)
except Exception as e:
    print('HttpBin', e)
a = time.time()
try:
    r = requests.get('http://www.baidu.com', proxies=proxies)
    b = time.time()
    if '京公网安备11000002000001号' in r.text:
        print(b - a)
except:
    print('baiduNo')
# print(r.text)  # '

# proxies = {
#     'http://': 'http://117.135.251.133:1234111'
# }
# r = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
