#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
import requests

proxies = {
    'http://': 'http://192.168.0.1:1234'
}
r = requests.get('http://httpbin.org/ip', proxies=proxies)
print(r.text)
print(r.status_code)

# of = open('proxy.txt', 'w')

# for page in range(1):
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Linux; U; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13'
#     }
#     url = 'http://www.xici.net.co/nn/' + str(page + 1)
#     r = requests.get(url, headers=headers)
#     html_doc = r.text
#     soup = BeautifulSoup(html_doc, 'lxml')
#     trs = soup.find('table', id='ip_list').find_all('tr')
#     for tr in trs[1:]:
#         tds = tr.find_all('td')
#         print(tds[2])
#         print(tds[3])
#         print(tds[5])
#         ip = tds[1].text.strip()
#         port = tds[2].text.strip()
#         protocol = tds[5].text.strip()

# of.close()
