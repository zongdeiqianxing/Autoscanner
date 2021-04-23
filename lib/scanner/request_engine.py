import requests

class Request():
    def __init__(self):
        self.proxy = {'http': 'http://127.0.0.1:7777',
                      'https': 'http://127.0.0.1:7777',}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0)',
                      }

    def repeat(self,url):
        try:
            response = requests.get(url=url,headers=self.headers,proxies=self.proxy,verify=False,timeout=20)
            #print(response)
            return response
        except Exception as e:
            print(e)


if __name__ =="__main__":
    X = Request()
    X.repeat("http://testphp.vulnweb.com:80/.idea/")


