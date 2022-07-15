import os
import tempfile
import sqlite3
import tldextract
from .Tools import *
from .urlParser import Parse
from .report import Report
from .db import db_insert
from loguru import logger
from queue import Queue


class Controller:
    def __init__(self, arguments):
        self.args = arguments.args
        self.subdomains = []
        self.logfile = tempfile.NamedTemporaryFile(delete=False).name
        self.log = {}
        self.xray = Xray()
        self.ports_result = {}
        self.is_url_scan = 0
        self.queue = Queue()

    def assign_task(self):
        def url_scan(urlList):
            if urlList:
                self.urlList = sorted(set(urlList), key=urlList.index)
                for _target in urlList:
                    db_insert('insert into target_info (target, batch_num) values (?,?);', _target, now_time)
                    _target = Parse(_target)                  # return dict{ip,domain,http_url}
                    if _target.data:
                        db_insert('insert into scanned_info (domain, batch_num) values (?,?)', _target.data['http_url'], now_time)
                        self.web_scan(_target)
                        if self.is_url_scan == 1:
                            Report().update_report(_target)

        self.xray.passive_scan()

        if self.args.urlList:
            self.is_url_scan = 1
            url_scan(self.args.urlList)
            self.is_url_scan = 0

        if self.args.domainList:
            self.args.domainList = sorted(set(self.args.domainList), key=self.args.domainList.index)
            for domain in self.args.domainList:
                if not Parse.isIP(domain):
                    if Parse(domain).data:      # 域名存在解析不成功的情况
                        self.subdomains = self.subdomains_scan(Parse(domain).data['domain'])
                        for subdomain in self.subdomains:
                            if tldextract.extract(subdomain)[0]:       # 如果子域名部分为空就不扫了，因为肯定有www.形式的
                                target = Parse(subdomain)
                                print(target)
                                if target.data:
                                    db_insert('insert into host_info (domain, batch_num) values (?,?)', target.data['domain'], now_time)
                                    http_urls = self.ports_scan(target)
                                    url_scan(http_urls)
                                    Report().update_report(target)

                else:
                    target = Parse(domain)
                    db_insert('insert into host_info (domain, batch_num) values (?,?)', target.data['domain'], now_time)
                    http_urls = self.ports_scan(target)
                    url_scan(http_urls)
                    Report().update_report(target)

    def subdomains_scan(self, target):
        cmd = "python3 oneforall/oneforall.py --target {target} run".format(target=target)
        logfile = '{path}/oneforall/results/{target}.csv'.format(path=tool_path, target=target)
        oneforall = Oneforall(cmd=cmd, domain=target, logfile=logfile, verbose=self.args.verbose)
        return oneforall.data if oneforall.data else [target]

    def ports_scan(self, target):
        # 在线同ip网站查询
        bugscanner = Bugscanner(domain=target.data['domain'], verbose=self.args.verbose)
        if bugscanner.data:
            self.subdomains += [domain for domain in bugscanner.data if domain.strip() not in self.subdomains and
                                    tldextract.extract(target.data['domain'][1]) == tldextract.extract(domain)[1]]

        # 如果判断是cdn的话，跳过下面的mascan nmap
        nslookup = Nslookup(domain=target.data['domain'], verbose=self.args.verbose)
        if 'cdn' in nslookup.run_log:
            return [target.data['http_url']]

        rate = config.get('MASSCAN', 'RATE')
        cmd = "masscan --open -sS -Pn -p 1-20000 {target} --rate {rate}".format(target=target.data['ip'], rate=int(rate))
        masscan = Masscan(cmd=cmd, domain=target.data['ip'], verbose=self.args.verbose)

        # 可能存在防火墙等设备,导致扫出的端口非常多。当端口大于20个时，跳过忽略
        if not masscan.data or len(masscan.data) > 20:
            masscan.data = ['21', '22', '445', '80', '1433', '3306', '3389', '6379', '7001', '8080']

        # nmap 如果80和443同时开放，舍弃443端口
        _ = "nmap -sS -Pn -A -p {ports} {target_ip} -oN {logfile}".format(ports=','.join(masscan.data), target_ip=target.data['ip'], logfile=self.logfile)
        nmap = Nmap(_, self.logfile)
        if nmap.data:
            if 80 in nmap.data and 443 in nmap.data:
                nmap.data.remove(443)

        urls = ['{0}:{1}'.format(target.data['http_url'], port) for port in nmap.data if port]
        return urls

    def web_scan(self, target):
        # 如果curl访问网站出现问题，那么就跳过本次扫描。 并且nuclei会一直卡那儿
        result = os.popen('whatweb {}'.format(target.data['http_url'])).read()
        if 'curl: (7) Failed to ' in result and 'Connection refused' in result:
            logger.warning('{} cannot accessible')
            return

        # 主要查看组织， 是否是云服务器
        iplocation = IpLocation(domain=target.data['ip'], verbose=self.args.verbose)

        cmd = "whatweb --color never {}".format(target.data['http_url'])
        whatweb = Whatweb(cmd=cmd, verbose=self.args.verbose)

        # 截图
        snapshot = Snapshot(domain=target.data['http_url'])

        # nuclei   这儿主要下要下载模板文件到
        # cmd = 'nuclei -u {} -t {}/nuclei-templates-master/ -o {}'.format(target.data['http_url'], tool_path, self.logfile)
        if not self.args.ex_nuclei:
            cmd = 'nuclei -u {} --as -nc -nts -o {}'.format(target.data['http_url'], self.logfile)
            nuclei = Nuclei(cmd=cmd, domain=target.data['http_url'], verbose=self.args.verbose)

        # 注意--push-to-proxy必须是http协议, 更换chrome为静态包执行不了
        cmd = './crawlergo/crawlergo -c /usr/bin/google-chrome-stable -t 10 --push-to-proxy http://127.0.0.1:7777 -o json {}'.format(target.data['http_url'])
        crawlergo = Crawlergo(cmd=cmd, domain=target.data['http_url'], verbose=self.args.verbose)

        # crawlergo扫描出来的子域名动态添加到域名列表中
        if crawlergo.data:
            self.subdomains += [domain for domain in crawlergo.data if domain.strip() not in self.subdomains]

        # 等待xray扫描结束，因为各类工具都是多线程高并发，不等待的话xray会一批红：timeout
        if crawlergo.run_log:
            while True:
                if self.xray.wait_xray_ok():
                    break

        # 将dirsearch扫出的url添加到xray去
        cmd = 'python3 dirsearch/dirsearch.py -x 301,302,403,404,405,500,501,502,503 --full-url -u {target} --csv-report {logfile}'.format(
                    target=target.data['http_url'], logfile=self.logfile)
        dirsearch = Dirsearch(cmd=cmd, domain=target.data['http_url'], logfile=self.logfile, verbose=self.args.verbose)
        if dirsearch.data:
            for url in dirsearch.data:
                response = Request().repeat(url)











