import os
import tempfile
import sqlite3
from lib.Tools import *
from lib.urlParser import Parse
from lib.report import Report
from lib.db import db_insert

class Controller:
    def __init__(self, arguments):
        self.urls_target = arguments.urlList
        self.domains_target = arguments.domainList
        self.logfile = tempfile.NamedTemporaryFile(delete=False).name
        self.log = {}
        self.xray = Xray()

        if arguments.tools:
            self.toolsList = [tool for tool in arguments.tools.split(',')]

    def assign_task(self):
        def url_scan(urls_target):
            if urls_target:
                self.urls_target = sorted(set(self.urls_target), key=urls_target.index)
                for _target in urls_target:
                    db_insert('insert into target_info (target, batch_num) values (?,?);', _target, now_time)
                    _target = Parse(_target)                  # return dict{ip,domain,http_url}
                    if _target.data:
                        db_insert('insert into scanned_info (domain, batch_num) values (?,?)', _target.data['http_url'], now_time)
                        self.urls_scan(_target)
                    Report().html_report_single()

        self.xray.passive_scan()

        if self.urls_target:
            url_scan(self.urls_target)

        if self.domains_target:
            self.domains_target = sorted(set(self.domains_target), key=self.domains_target.index)
            for domain in self.domains_target:
                if not Parse.isIP(domain):
                    if Parse(domain).data:      # 域名存在解析不成功的情况
                        subdomains = self.subdomains_scan(Parse(domain).data['domain'])
                        for subdomain in subdomains:
                            target = Parse(subdomain)
                            print(target)
                            if target.data:
                                db_insert('insert into host_info (domain, batch_num) values (?,?)', target.data['domain'], now_time)
                                http_urls = self.ports_scan(target)
                                url_scan(http_urls)

                else:
                    target = Parse(domain)
                    db_insert('insert into host_info (domain, batch_num) values (?,?)', target.data['domain'], now_time)
                    http_urls = self.ports_scan(target)
                    url_scan(http_urls)

    def subdomains_scan(self, target):
        _ = "python3 oneforall/oneforall.py --target {target} run".format(path=tool_path, target=target)
        logfile = '{path}/oneforall/results/{target}.csv'.format(path=tool_path, target=target)
        oneforall = Oneforall(_, logfile)
        return oneforall.data if oneforall.data else [target]

    def ports_scan(self, target):
        nslookup = Nslookup(target.data['domain'])

        cdns = ['cdn', 'kunlun', 'bsclink.cn', 'ccgslb.com.cn', 'dwion.com', 'dnsv1.com', 'wsdvs.com', 'wsglb0.com', 'lxdns.com', 'chinacache.net.', 'ccgslb.com.cn', 'aliyun']
        for cdn in cdns:
            if cdn in nslookup.log:
                print('maybe the {} is cdn'.format(target.data['domain']))
                print(nslookup.log)
                return [target.data['http_url']]

        _ = "masscan --open -sS -Pn -p 1-20000 {target} --rate 2000".format(target=target.data['ip'])
        masscan = Masscan(_, None)

        '''
        可能存在防火墙等设备,导致扫出的端口非常多
        '''
        if not masscan.data or len(masscan.data) > 20:
            masscan.data = ['21', '22', '445', '80', '1433', '3306', '3389', '6379', '7001', '8080']

        '''
        nmap 如果80和443同时开放，舍弃443端口
        '''
        _ = "nmap -sS -Pn -A -p {ports} {target_ip} -oN {logfile}".format(ports=','.join(masscan.data), target_ip=target.data['ip'], logfile=self.logfile)
        nmap = Nmap(_, self.logfile)
        if nmap.data:
            if 80 in nmap.data and 443 in nmap.data:
                nmap.data.remove("443")
            return ['{}:{}'.format(target.data['http_url'], port) for port in nmap.data]

        return [target.data['http_url']]

    def urls_scan(self, target):
        # 主要查看组织， 是否是云服务器
        iplocation = IpLocation(target.data['ip'])

        _ = "whatweb --color never {}".format(target.data['http_url'])
        whatweb = Whatweb(_)

        # 截图
        snapshot = Snapshot(target.data['http_url'])

        '''
        crawlergo
        扫描出来的子域名动态添加到域名列表中
        注意--push-to-proxy必须是http协议, 更换chrome为静态包执行不了
        '''
        _ = './crawlergo -c /usr/bin/google-chrome-stable -t 10 --push-to-proxy http://127.0.0.1:7777 -o json {}'.format(target.data['http_url'])
        crawlergo = Crawlergo(_)

        if crawlergo.data:
            if self.domains_target:
                self.domains_target += [domain for domain in crawlergo.data if domain not in self.domains_target]

        '''
        等待xray扫描结束，因为各类工具都是多线程高并发，不等待的话xray会一批红：timeout
        '''
        if crawlergo.log:
            print('xray start scanning')
            while True:
                if self.xray.wait_xray_ok():
                    break

        '''
        将dirsearch扫出的url添加到xray去
        '''
        _ = 'python3 dirsearch/dirsearch.py -x 301,302,403,404,405,500,501,502,503 --full-url -u {target} --csv-report {logfile}'.format(
                    target=target.data['http_url'], logfile=self.logfile)
        dirsearch = Dirsearch(_, self.logfile)

        if dirsearch.data:
            for url in dirsearch.data:
                response = Request().repeat(url)













