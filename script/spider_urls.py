'''
根据第一个域名爬取href链接，并以此循环爬取
python3 spider_urls.py
'''

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0)',}


class Spider:
    def __init__(self, begin_url):
        self.domains = set()
        self.urls = []
        self.urls.append(begin_url)

    def parse_url(self):
        for url in self.urls:
            try:
                response = requests.get(url=url, headers=HEADERS, timeout=10)
                if response.status_code == 200 and response.text:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for href in soup.find_all('a'):
                        try:
                            href = href.get('href').strip('/')
                            if href.startswith('http'):
                                print(urlparse(href).netloc)
                                if urlparse(href).netloc not in self.domains:
                                    self.domains.add(urlparse(href).netloc)
                                    self.urls.append(href)
                        except Exception as e:
                            continue
            except Exception as e:
                self.output()
                continue

            if len(self.urls) > 100000:
                self.output()
                exit(1)

    def output(self):
        with open('urls.txt', 'w') as f:
            for i in self.urls:
                f.write(i+'\n')


Spider('http://www.js-jinhua.com/').parse_url()
