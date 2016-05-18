import requests
url = 'http://www.cnhan.com/w/20160515/372463.htm'
rep = requests.get(url)
rep.encoding = 'utf-8'

with open('request.html', 'w', encoding='utf-8') as f:
    f.writelines(rep.text)
print('第一')
from selenium import webdriver
drvier = webdriver.PhantomJS()
drvier.maximize_window()
print("进")
drvier.get('http://www.cnhan.com/w/20160515/372463.htm')
print('获取')
html = drvier.page_source
drvier.quit()
print('===退')
with open('phantomjs.html', 'w', encoding='utf-8') as f:
    f.writelines(html)
