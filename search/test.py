import requests
proxies = {'http': 'http://64.37.115.5:8080'}
r = requests.get('https://www.sogou.com/web?query=inurl:install/index.php&page=7', proxies=proxies)
r.encoding = 'utf-8'
with open('gggg.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
