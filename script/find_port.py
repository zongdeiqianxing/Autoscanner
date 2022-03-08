'''
        usage: python3 find_port.py 1.txt
        功能： 寻找开放某个端口的资产，导入资产文件中无论是url还是ip还是域名都可以
'''
import socket
import queue
import threading
import sys
from socket import gethostbyname_ex
from IPy import IP
from urllib.parse import urlparse


PORT = 80
class PortScan:
    def __init__(self, file):
        self.file = file
        self.ips = queue.Queue()
        self.readfile()
        self.threads_run()

    def readfile(self):
        with open(self.file, 'r') as f:
            for url in f.readlines():
                target = Parse(url)
                if target.data:
                    self.ips.put(target.data['ip'])

    def threads_run(self):
        for i in range(20):
            t = threading.Thread(target=self.check_port, )
            t.start()

    def check_port(self):
        while True:
            if self.ips.empty():
                exit('empty')

            ip = self.ips.get()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((ip, PORT))
                s.settimeout(3)
                s.close()
                print(ip)
                return True
            except socket.error as e:
                return False


class Parse:
    def __init__(self,target):
        if self.isIP(target):
            self.data = {
                'ip': target,
                'domain': None,
                'http_url': 'http://' + target,
            }

        elif target.startswith('http'):
            netloc = urlparse(target).netloc
            if self.isIP(netloc):
                self.data = {
                    'ip': netloc,
                    'domain': None,
                    'http_url': target,
                }
            else:
                try:
                    data = list(gethostbyname_ex(netloc))
                    self.data = {'ip': data[2][0],
                                 'domain': netloc,
                                 'http_url': target,
                                }
                except:
                    self.data = None

    def isIP(self, str):
        try:
            IP(str)
        except ValueError:
            return False
        return True


if __name__ == '__main__':
    if not sys.argv[1]:
        print('''
        usage: python3 find_port.py 1.txt
        
        功能： 寻找开放某个端口的资产，导入资产文件中无论是url还是ip还是域名都可以
        ''')

    a = PortScan(sys.argv[1])
