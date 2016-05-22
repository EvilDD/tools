# import requests
# url = 'http://www.bbinbo.com'
# rep = requests.get(url)
# # rep.encoding = 'utf-8'

# with open('request1.html', 'w', encoding='utf-8') as f:
#     f.writelines(rep.text)
# print('第一')
# from selenium import webdriver
# drvier = webdriver.Chrome()
# drvier.maximize_window()
# print("进")
# drvier.get(url)
# print('获取')
# html = drvier.page_source
# drvier.quit()
# print('===退')
# with open('phantomjs1.html', 'w', encoding='utf-8') as f:
#     f.writelines(html)
import re
with open('phantomjs.html', 'r', encoding='utf-8') as f:
    html = f.read()
rule = re.compile('"http://.*?"')
urls = re.findall(rule, html)
for url in urls:
    pass
