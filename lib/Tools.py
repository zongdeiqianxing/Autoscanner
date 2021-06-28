import os
import re
import csv
import logging.config
import simplejson
import subprocess
import requests
import tempfile
import threading
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lib.db import db_update

now_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
logging.config.fileConfig(os.path.join(main_path, "config/logging.ini"))
tool_path = os.path.join(main_path,'tools')
XRAY_LISTEN_PORT = 7777                                 # 改动的话需要注意controller里面crawlergo推送也要改


class Tools:
    def __init__(self, command, logfile=None):
        self.command = command
        self.logfile = logfile
        self.log = None             # 存放工具原日志
        self.data = None            # 存放自定义删选后的数据
        self.logger = logging.getLogger('toolConsole')
        self.scan()
        self.filter_log()
        self.db_update()

    def scan(self):
        self.logger.info(self.__class__.__name__ + ' - ' + ' start scanning ! ')
        try:
            _ = subprocess.run(self.command, shell=True, timeout=400, cwd=tool_path, stdout=subprocess.PIPE)
            self.log = str(_.stdout, encoding='utf-8')
            print(self.log)
            if self.logfile:
                self.read_report_file()
        except Exception as e:
            self.log = None
            self.kill_process()
            self.logger.error(self.__class__.__name__ + ' - ' + str(e))
        self.logger.info(self.__class__.__name__ + ' - ' + ' scanned over ! ')

    def read_report_file(self):
        if self.logfile and os.path.exists(self.logfile):
            with open(self.logfile) as f:
                self.log = f.read()

    def filter_log(self):
        pass

    def kill_process(self):
        _ = "ps aux | grep '{name}'|grep -v 'color' | awk '{{print $2}}'".format(name=self.__class__.__name__.lower())
        process = os.popen(_).read()
        if process:
            os.popen('nohup kill -9 {} 2>&1 &'.format(process.replace('\n', ' ')))

    # 需要在main.py中创建列，在controller中调用
    # 默认记录url扫描的工具日志，其他如端口日志需要重构
    def db_update(self):
        if self.log:
            db_update('scanned_info', self.__class__.__name__.lower(), self.log)

            # with sqlite3.connect(os.path.join(main_path, 'scanned_info.db')) as conn:
            #     sql = 'update scanned_info set {}=? order by id desc limit 1;'.format(self.__class__.__name__.lower())
            #     conn.execute(sql, (self.log,))     # 插入时必须是str


'''
oneforall 
扫描所有子域名并筛选去重出所有子域名
'''
class Oneforall(Tools):
    def filter_log(self):
        try:
            if self.logfile and os.path.exists(self.logfile):
                with open(self.logfile, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    column = [row[5] for row in reader]
                    del column[0]
                    self.data = list(set(column))
                    self.log = '\n'.join(self.data)
        except Exception as e:
            print(e)

    def db_update(self):
        if self.log:
            db_update('target_info', self.__class__.__name__.lower(), self.log)


'''
nslookup ,  查看是否有cdn
'''
class Nslookup(Tools):
    def scan(self):
        # IBM 阿里云 中国互联网络信息中心
        dns = ['9.9.9.9', '223.5.5.5', '1.2.4.8']
        self.log = ''
        for _dns in dns:
            r = os.popen('nslookup {t} {d}'.format(t=self.command, d=_dns)).read()
            r = r.split('\n')[4:]
            self.log += ('\n'.join(r))
        print(self.log)
        
    def db_update(self):
        if self.log:
            db_update('host_info', self.__class__.__name__.lower(), self.log)


'''
查询ip定位 主要看是不是云服务器
'''
class IpLocation(Tools):
    def scan(self):
        # 此处IP和域名都行
        url = 'http://demo.ip-api.com/json/{ip}'.format(ip=self.command)
        resp = Request().get(url)
        if resp and resp.json():
            self.log = ''
            r = resp.json()
            l = ['status', 'country', 'city', 'isp', 'org', 'asname', 'mobile']
            for k, v in r.items():
                if k in l:
                    print('{}: {}'.format(k, r[k]))
                    self.log += '{}: {}'.format(k, r[k]) + '\n'

    def db_update(self):
        if self.log:
            db_update('host_info', self.__class__.__name__.lower(), self.log)


'''
masscan
调用self.data获取返回的ports list
masscan 只接收ip作为target
'''
class Masscan(Tools):
    def filter_log(self):
        if self.log:
            ports = re.findall('\d{1,5}/tcp', self.log)
            self.data = [x[:-4] for x in ports]

    def db_update(self):
        if self.log:
            db_update('host_info', self.__class__.__name__.lower(), self.log)


'''
nmap
遍历所有http https端口
'''
class Nmap(Tools):
    def filter_log(self):
        if self.log:
            http_ports = re.findall('\d{1,5}/tcp\s{1,}open\s{1,}[ssl/]*http', self.log)
            http_ports = [int(x.split("/")[0]) for x in http_ports]
            self.data = http_ports

    def db_update(self):
        if self.log:
            db_update('host_info', self.__class__.__name__.lower(), self.log)


'''
whatweb
'''
class Whatweb(Tools):
    def filter_log(self):
        if self.log:
            log = []
            if '\n' in self.log.strip('\n'):
                self.log = self.log.split('\n')[0]

            keys = ['IP', 'Title', 'PoweredBy', 'HTTPServer', 'X-Powered-By', 'Meta-Refresh-Redirect', 'Cookies']
            for _ in self.log.split(','):
                for key in keys:
                    if _.strip().startswith(key):
                        log.append(_)
            self.log = '\n'.join(log)


'''
crawlergo
发现的子域名将在controller模块中动态去重添加进入扫描
'''
class Crawlergo(Tools):
    def scan(self):
        try:
            rsp = subprocess.run(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300, shell=True, cwd=tool_path)
            output = str(rsp.stdout, encoding='utf-8')
            result = simplejson.loads(output.split("--[Mission Complete]--")[1])
            req_list = result["req_list"]
            urls = []
            for req in req_list:
                urls.append(req['url'] + '    ' + req['data'])
            subdomains = result["sub_domain_list"]
            domain = self.command.split()[-1]
            self.data = self.filter_domain(domain, subdomains)
            self.log = urls + ['\n'*2] + subdomains
            self.log = '\n'.join(self.log)
            print(self.log)
        except Exception as e:
            self.log = None
            self.logger.error(self.__class__.__name__ + ' - ' + str(e))
        finally:
            self.kill_process()  # 可能还会余留chrome进程，为了避免杀掉用户的chrome，暂时保留

    # crawlergo 在获取sub_domain_list时 在获取xx.com.cn这种3级域名时会默认com.cn为base域名
    @staticmethod
    def filter_domain(domain, domains):
        if domains:
            if domain.count('.') > 2:
                domain = domain.split('.', 1)[1]
            for _ in domains:
                if domain not in _:
                    domains.remove(_)
        return domains

class Xray:
    def __init__(self):
        self.logfile = os.path.join(main_path, 'report/{}-xray.html'.format(now_time))
        self.backup_file = tempfile.NamedTemporaryFile(delete=False).name
        self.proxy = '127.0.0.1:{}'.format(XRAY_LISTEN_PORT)
        self.kill_exists_process()
        self.xray_wait_time = 0

    def passive_scan(self):
        def xray_passive():
            _ = "{path}/tools/xray_linux_amd64 webscan --listen {proxy} --html-output {logfile} | tee -a {backup_file}"\
                .format(path=main_path, proxy=self.proxy, logfile=self.logfile, backup_file=self.backup_file)
            os.system(_)

        t = threading.Thread(target=xray_passive, daemon=True)
        t.start()

    def initiative_scan(self, url):
        def xray_initiative(u):
            _ = "{path}/tools/xray_linux_amd64 webscan --basic-crawler {url} --html-output {logfile}.html" \
                .format(path=main_path, url=u, logfile=self.logfile)
            os.system(_)

        t = threading.Thread(target=xray_initiative, args=(url,), daemon=True)
        t.start()

    def wait_xray_ok(self):
        __ = '''
                wc {0} | awk '{{print $1}}';
                sleep 5;
                wc {0} | awk '{{print $1}}';
            '''.format(self.backup_file)
        result = os.popen(__).read()

        if result.split('\n')[0] == result.split('\n')[1]:
            _ = "tail -n 10 {}".format(self.backup_file)
            s = os.popen(_).read()

            if "All pending requests have been scanned" in s:
                os.system('echo "" > {}'.format(self.backup_file))
                return True

            if self.xray_wait_time == 2:
                return True
            else:
                self.xray_wait_time += 1
        return False

    def kill_exists_process(self):
        process = os.popen("ps aux | grep 'xray'|grep -v 'color' | awk '{print $2}'").read()
        if process:
            os.popen('nohup kill -9 {} 2>&1 &'.format(process.replace('\n', ' ')))


'''
dirsearch v0.4.1
'''
class Dirsearch(Tools):
    def read_report_file(self):
        self.log, self.data = [], []
        with open(self.logfile, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            if lines:
                lines.pop(0)

                for line in lines:
                    line = line.split(',')
                    try:
                        s = "{:<}  - {:>5}B  -  {:<5}".format(line[2], line[3], line[1])
                        self.log.append(s)
                        self.data.append(line[1])
                    except Exception as e:
                        print(e)
                        continue

        self.log = '\n'.join(self.log)


'''
requests请求，将dirsearch扫描出的url推到xray
'''
class Request:
    def __init__(self,):
        self.proxy = {'http': 'http://127.0.0.1:{}'.format(XRAY_LISTEN_PORT),
                      'https': 'http://127.0.0.1:{}'.format(XRAY_LISTEN_PORT)}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0)',
                        }

    def repeat(self, url):
        try:
            response = requests.get(url=url, headers=self.headers, proxies=self.proxy, verify=False, timeout=20)
            # print(response)
            return response
        except Exception as e:
            print(e)

    def get(self, url):
        try:
            response = requests.get(url=url, headers=self.headers, verify=False, timeout=20)
            return response
        except Exception as e:
            print(e)


'''
截图， 考虑base64加到html里整个报告太大了，所以只能保存到本地，然后使用img src
暂时不写入db
'''
class Snapshot(Tools):
    def scan(self):
        option = Options()
        option.add_argument('--headless')
        option.add_argument('--no-sandbox')
        option.add_argument('--start-maximized')

        try:
            driver = webdriver.Chrome(chrome_options=option)
            driver.set_window_size(1366, 768)
            driver.implicitly_wait(4)
            driver.get(self.command)
            time.sleep(1)
            driver.get_screenshot_as_file(os.path.join(main_path, 'report/img/{}.png'.format(self.format_img_name(self.command))))
            driver.quit()
        except Exception as e:
            pass

    @staticmethod
    def format_img_name(url):
        if url.startswith('http'):
            url = url.split('/')[2]
            if ':' in url:
                url = url.replace(':', '_')
            return url

