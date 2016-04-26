#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from crawlerData import mySql


def diggerIp():
    proxysIp = []  # 代理ip信息
    driver = webdriver.PhantomJS()
    driver.get('http://www.site-digger.com/html/articles/20110516/proxieslist.html')
    soup = BeautifulSoup(driver.page_source, 'lxml')
    driver.quit()
    iptrs = soup('tr')
    ipRule = '</script>(.*?)</td>'  # ip:prot
    ipR = '(.*?):'  # 拆分出ip
    portR = ':(\d+)'
    tpRule = ':\d+</td>\n<td>(.*?)</td>'  # 类型Transparent，Anonymous
    ctRule = ':\d+</td>\n<td>.*?</td>\n<td>(\w+)'  # 国家 China
    toRule = '<th>(\d+)</th>'  # 延时
    del iptrs[0]
    for iptr in iptrs:
        ipMes = []  # ip,匿名类型,国家,延时
        iptr = repr(iptr)
        ipPort = re.findall(ipRule, iptr)
        if ipPort != []:  # 只要ip不为空就添加列表,主要是ip
            ip = re.findall(ipR, ipPort[0])
            ipMes.append(ip[0])  # 加ip到列表
            port = re.findall(portR, ipPort[0])
            ipMes.append(port[0])  # 加prot到列表
            tp = re.findall(tpRule, iptr)
            if tp != []:
                ipMes.append(tp[0])  # 加类型到列表
            ct = re.findall(ctRule, iptr)
            if ct != []:
                ipMes.append(ct[0])  # 加地域到列表
            to = re.findall(toRule, iptr)
            if to != []:
                ipMes.append(to[0])  # 加延时到列表
        proxysIp.append(ipMes)
    return proxysIp  # [[ip,type,country,timeout],[]]


def main():
    ipList = diggerIp()
    db = mySql()
    db.insertData(ipList)

if __name__ == '__main__':
    main()
