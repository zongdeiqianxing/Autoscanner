# coding:utf8

import os
import re
import csv
import itertools
import simplejson
import subprocess
import requests
import tempfile
import threading
import configparser
import sqlite3
import time
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lib.db import db_update
from bs4 import BeautifulSoup

config = configparser.RawConfigParser()
now_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]

config.read(os.path.join(main_path, 'config', 'config.ini'))
# log_path = config.get('Tools_logfile', 'path')
# logfile = config.get('Tools_logfile', 'file').format(date=time.strftime(config.get('Tools_logfile', 'date'), time.localtime(time.time())))

tool_path = os.path.join(main_path, 'tools')
XRAY_LISTEN_PORT = int(config.get('XRAY', 'XRAY_LISTEN_PORT'))
ZOOM_API_KEY = config.get('ZOOMEYE', 'API_KEY')
timeout = config.get('Tools_timeout', 'timeout')


'''
所有工具类的模板
run_logfile 是有些工具会直接输出报告文件的，需要对报告文件操作，如oneforall、dirsearch
archive_logfile 是
'''
class Tools:
    def __init__(self, cmd='', domain='', verbose=False, logfile=None):
        self.cmd = cmd
        self.domain = domain
        self.verbose = verbose
        self.logfile = logfile      # 存放工具默认需要生成文件的，如dirsearch
        self.run_log = None         # 存放工具运行日志
        self.data = None            # 存放自定义删选后的数据

        logger.info('{} - {} - start scanning'.format(self.domain, self.__class__.__name__))
        self.scan()
        self.filter_log()
        self.db_update()

        if self.verbose:
            print(self.run_log)
        logger.info('{} - {} - over'.format(self.domain, self.__class__.__name__))

    def scan(self):
        try:
            _ = subprocess.run(self.cmd, shell=True, timeout=int(timeout), cwd=tool_path, stdout=subprocess.PIPE)
            self.run_log = str(_.stdout, encoding='utf8')
            if self.logfile:
                self.read_report_file()
        except subprocess.TimeoutExpired as e:
            self.run_log = 'Timed Out'
            logger.error('{} - {} - \n{}'.format(self.domain, self.__class__.__name__, e))
        except Exception as e:
            logger.error('{} - {} - \n{}'.format(self.domain, self.__class__.__name__, e))
        finally:
            self.kill_process()

    def read_report_file(self):
        if self.logfile and os.path.exists(self.logfile):
            with open(self.logfile) as f:
                self.run_log = f.read()

    def filter_log(self):
        pass

    def kill_process(self):
        _ = "ps aux | grep '{name}'|grep -v 'color' | awk '{{print $2}}'".format(name=self.__class__.__name__.lower())
        process = os.popen(_).read()
        print(process)
        if process:
            os.popen('nohup kill -9 {} 2>&1 &'.format(process.replace('\n', ' ')))

    # 需要在main.py中创建列，在controller中调用
    # 默认记录url扫描的工具日志，其他如端口日志需要重构
    def db_update(self):
        if self.run_log:
            db_update('scanned_info', self.__class__.__name__.lower(), self.run_log)

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
                    print(self.data)
                    self.run_log = '\n'.join(self.data)
        except Exception as e:
            logger.error('{} - {} - \n{}'.format(self.domain, self.__class__.__name__, e))

    def db_update(self):
        if self.run_log:
            db_update('target_info', self.__class__.__name__.lower(), self.run_log)


class Zoomeye(Tools):           # need domain
    def check_run(self):
        if ZOOM_API_KEY :
            try:
                os.popen('zoomeye init -apikey "{}"'.format(ZOOM_API_KEY))
            except Exception as e:
                logger.error('{} - {} - \n{}'.format(self.domain, self.__class__.__name__, e))
        else:
            logger.error('zoomeye工具需要api_key,  本次将跳过zoomeye扫描，在config.ini中输入后再次开启扫描')
            time.sleep(5)

    def scan(self):
        self.check_run()
        self.data = []
        for page in itertools.count(1, 1):
            try:
                cmd = 'python3 zoomeye/zoomeye/cli.py domain -page {p} {d} 1'.format(p=page, d=self.domain)
                _ = subprocess.run(cmd, shell=True, timeout=int(timeout), cwd=tool_path, stdout=subprocess.PIPE)
                r = str(_.stdout, encoding='gbk')
                for line in r.splitlines():
                    line = re.sub('\x1b.*?m', '', line)
                    line = [_ for _ in line.split(' ') if _]
                    # print(line)

                    if line and 'name' in line and 'timestamp' in line:
                        continue
                    if line:
                        if line[0].startswith('total'):
                            if line[1] and int(int(line[1].split('/')[1])/int(line[1].split('/')[0]))+1 == i:
                                return  # scan over
                        else:
                            self.data.append(line[0])
            except BrokenPipeError:
                pass
            except Exception as e:
                logger.error('{} - {} - \n{}'.format(self.domain, self.__class__.__name__, e))
        self.run_log = '\n'.join(self.data)

    def db_update(self):
        if self.run_log:
            db_update('target_info', self.__class__.__name__.lower(), self.run_log)


'''                                                                                                                                                                                                                                       
nslookup ,  查看是否有cdn
'''
class Nslookup(Tools):
    def scan(self):
        # IBM 阿里云 中国互联网络信息中心
        dns = ['9.9.9.9', '223.5.5.5', '1.2.4.8']
        self.run_log = ''
        for _dns in dns:
            r = os.popen('nslookup {domain} {d}'.format(domain=self.domain, d=_dns)).read()
            r = r.split('\n')[4:]
            self.run_log += ('\n'.join(r))

    def filter_log(self):
        cdns = ['cdn', 'kunlun', 'bsclink.cn', 'ccgslb.com.cn', 'dwion.com', 'dnsv1.com', 'wsdvs.com', 'wsglb0.com',
                'lxdns.com', 'chinacache.net.', 'ccgslb.com.cn', 'aliyun']
        for cdn in cdns:
            if cdn in self.run_log:
                # print('maybe the {} is cdn'.format(target.data['domain']))
                # print(nslookup.run_log)
                logger.warning("{} may be is cdn, scan will be skipped")
                self.run_log += '\n可能存在cdn：{}'.format(cdn)

    def db_update(self):
        if self.run_log:
            db_update('host_info', self.__class__.__name__.lower(), self.run_log)


'''
查询ip定位 主要看是不是云服务器
'''
class IpLocation(Tools):
    def scan(self):
        # 此处IP和域名都行
        url = 'http://demo.ip-api.com/json/{ip}'.format(ip=self.domain)
        resp = Request().get(url)
        if resp and resp.json():
            self.run_log = ''
            r = resp.json()
            l = ['status', 'country', 'city', 'isp', 'org', 'asname', 'mobile']
            for k, v in r.items():
                if k in l:
                    self.run_log += '{}: {}'.format(k, r[k]) + '\n'

    def db_update(self):
        if self.run_log:
            db_update('host_info', self.__class__.__name__.lower(), self.run_log)


'''
masscan
调用self.data获取返回的ports list
masscan 只接收ip作为target
'''
class Masscan(Tools):
    def filter_log(self):
        if self.run_log:
            ports = re.findall('\d{1,5}/tcp', self.run_log)
            self.data = [x[:-4] for x in ports]

    def db_update(self):
        if self.run_log:
            db_update('host_info', self.__class__.__name__.lower(), self.run_log)


'''
nmap
遍历所有http https端口
'''
class Nmap(Tools):
    def filter_log(self):
        if self.run_log:
            http_ports = re.findall('\d{1,5}/tcp\s{1,}open\s{1,}[ssl/]*http', self.run_log)
            http_ports = [int(x.split("/")[0]) for x in http_ports]
            self.data = http_ports

    def db_update(self):
        if self.run_log:
            db_update('host_info', self.__class__.__name__.lower(), self.run_log)


class Bugscanner(Tools):            # need domain
    def scan(self):
        try:
            data = ''
            url = "http://dns.bugscaner.com/{}.html".format(self.domain)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36 Edg/98.0.1108.43'}
            resp = requests.get(url=url, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.title.string
            data += title + '\n'
            # print(title)
            # description =soup.find(attrs={"name": "description"})['content']
            # print(description)
            tables = soup.find_all('table', class_="table table-bordered")
            trs = tables[0].find_all('tr')
            for tr in trs:
                row = []
                cells = tr.find_all('th')
                if not cells:
                    cells = tr.find_all('td')
                for cell in cells:
                    row.append(cell.get_text())
                data += '{:>2}\t{:>30}\t{:>5}\t{:>10}\t{:>10}\n'.format(row[0], row[1], row[2], row[3], row[4])
            self.data = [data]
            self.run_log = data  # 在写入时候需要转换成''.join(data)形式，不然不会换行
        except requests.exceptions.ConnectionError:
            self.data = 'Time out'
        except Exception as e:
            pass

    def db_update(self):
        if self.run_log:
            db_update('host_info', self.__class__.__name__.lower(), self.run_log)

'''
whatweb
'''
class Whatweb(Tools):
    def filter_log(self):
        if self.run_log:
            log = []
            if '\n' in self.run_log.strip('\n'):
                self.run_log = self.run_log.split('\n')[0]

            keys = ['IP', 'Title', 'PoweredBy', 'HTTPServer', 'X-Powered-By', 'Meta-Refresh-Redirect', 'Cookies']
            for _ in self.run_log.split(','):
                for key in keys:
                    if _.strip().startswith(key):
                        log.append(_)
            self.run_log = '\n'.join(log)


'''
nuclei
nuclei -u http://192.168.64.128:8080/ -t `pwd`/nuclei-templates-master/ -o xx.log

controller中调用Nuclei之前要先使用curl http://192.168.64.128:8080判断端口是否开放，没开放的会nuclei会卡那。
curl: (7) Failed to connect to 192.168.64.128 port 80: Connection refused
'''
class Nuclei(Tools):
    pass


'''
crawlergo
发现的子域名将在controller模块中动态去重添加进入扫描
'''
class Crawlergo(Tools):
    def scan(self):
        try:
            rsp = subprocess.run(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=int(timeout), shell=True, cwd=tool_path)
            output = str(rsp.stdout, encoding='utf-8')
            result = simplejson.loads(output.split("--[Mission Complete]--")[1])
            req_list = result["req_list"]
            urls = []
            for req in req_list:
                urls.append(req['url'] + '    ' + req['data'])
            subdomains = result["sub_domain_list"]
            #domain = self.cmd.split()[-1]
            domain = self.domain
            self.data = self.filter_domain(domain, subdomains)
            self.run_log = urls + ['\n'*2 + 'crawlergo扫描的域名：'] + subdomains
            self.run_log = '\n'.join(self.run_log)
            # print(self.run_log)
        except Exception as e:
            logger.error(self.__class__.__name__ + ' - ' + str(e))
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

    def db_update(self):
        if self.run_log:
            db_update('target_info', self.__class__.__name__.lower(), ','.join(self.data))
            db_update('scanned_info', self.__class__.__name__.lower(), self.run_log)


class Xray:
    def __init__(self):
        self.logfile = os.path.join(main_path, 'report/{}-xray.html'.format(now_time))
        self.backup_file = tempfile.NamedTemporaryFile(delete=False).name
        self.proxy = '127.0.0.1:{}'.format(XRAY_LISTEN_PORT)
        self.kill_exists_process()
        self.xray_wait_time = 0

    def passive_scan(self):
        def xray_passive():
            cmd = "{path}/tools/xray_linux_amd64/xray_linux_amd64 webscan --listen {proxy} --html-output {logfile} | tee -a {backup_file}"\
                .format(path=main_path, proxy=self.proxy, logfile=self.logfile, backup_file=self.backup_file)
            os.popen(cmd)

        t = threading.Thread(target=xray_passive, daemon=True)
        t.start()

    def initiative_scan(self, url):
        def xray_initiative(u):
            cmd = "{path}/tools/xray_linux_amd64 webscan --basic-crawler {url} --html-output {logfile}.html" \
                .format(path=main_path, url=u, logfile=self.logfile)
            os.system(cmd)

        t = threading.Thread(target=xray_initiative, args=(url,), daemon=True)
        t.start()

    def wait_xray_ok(self):
        cmd = '''
                wc {0} | awk '{{print $1}}';
                sleep 5;
                wc {0} | awk '{{print $1}}';
            '''.format(self.backup_file)
        result = os.popen(cmd).read()

        if result.split('\n')[0] == result.split('\n')[1]:
            cmd = "tail -n 10 {}".format(self.backup_file)
            s = os.popen(cmd).read()

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
        self.run_log, self.data = [], []
        with open(self.logfile, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
            if lines:
                lines.pop(0)

                for line in lines:
                    line = line.split(',')
                    try:
                        s = "{:<}  - {:>5}B  -  {:<5}".format(line[2], line[3], line[1])
                        self.run_log.append(s)
                        self.data.append(line[1])
                    except Exception as e:
                        logger.error('{} - {} - \n{}'.format(self.domain, self.__class__.__name__, e))
                        continue
        self.run_log = '\n'.join(self.run_log)


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
            driver.get(self.domain)
            time.sleep(1)
            driver.get_screenshot_as_file(os.path.join(main_path, 'report/img/{}.png'.format(self.format_img_name(self.domain))))
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

