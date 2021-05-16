import os
import time
import re
from lib.general import url_parse,get_ip_from_url
from lib.scanner.oneforall import OneForAll
from lib.scanner import xray,crawlergo,nmap,masscan,dirsearch,awvs,request_engine,whatweb

class Controller():
    def __init__(self,arguments):
        self.arguments = arguments
        self.scanned_domains = []

        if self.arguments.args.restore:
            exit("restore exit ")

    def assign_task(self):
        self.init_report()

        self.xray = xray.Xray()
        self.xray.scan()

        for http_url in self.format_url():
            print("scanning : ",http_url)

            if self.arguments.args.fastscan:         # fastscan模式只web扫描，并且不重复添加扫描到的子域名
                self.url_scan(http_url)
                continue

            if http_url.count(":") < 2 and http_url.count("/") < 3 : # if like http://a.com:8080 or http://xx.com/1.php ,do self.url_scan()
                ip = get_ip_from_url(http_url)
                if not ip :
                    continue

                open_ports = masscan.Masscan(ip).open_ports
                if not open_ports or len(open_ports) > 20:
                    self.url_scan(http_url)
                    continue

                http_open_ports = nmap.Nmap(url_parse(http_url).get_netloc(),open_ports).http_open_ports        #use domain not ip in order to report

                if http_open_ports:
                    for port in http_open_ports:
                        http_url_with_port = http_url + ":" + port
                        self.url_scan(http_url_with_port)
                else:
                    print("nmap not found http server port at : ",http_url)
            else:
                self.url_scan(http_url)


    def url_scan(self,target):
        whatweb.Whatweb(target)

        c = crawlergo.Crawlergo(target)
        if c.sub_domains and not self.arguments.args.fastscan :                                        #将crawlergo扫描出的子域名添加到任务清单中
            print("crawlergo found domains : ",c.sub_domains)
            for domains in c.sub_domains:
                if domains not in self.arguments.urlList:
                    self.arguments.urlList.append(domains)

        time.sleep(5)
        print("waiting xray scan to end")
        while (True):                                                #wait for xray end scan
            if self.xray.check_xray_status():
                break

        urls = dirsearch.Dirsearch(target).urls
        if urls:
            request = request_engine.Request()                      #repeat urls found by dirsearch to xray
            for url in urls:
                request.repeat(url)
            time.sleep(5)

        if "awvs" in self.arguments.toolList:
            awvs.Awvs(target)

        self.scanned_domains.append(target)

    # 使用oneforall遍历子域名
    def format_url(self):
        for url in self.arguments.urlList:
            result = re.search(r'(([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}([01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])', url)
            if result:
                url = result.group()
                http_url = url_parse(url).get_http_url()  #
                yield http_url

            elif url.startswith('http'):
                yield url

            else:
                # 判断域名是否已经扫描过，包括含有http这类的链接
                scanned_status = False
                compile = '^[http://|https://]*' + url
                for u in self.scanned_domains:
                    if re.findall(compile,u):
                        print("{} had in scanned_domains list .".format(url))
                        scanned_status = True
                        break

                if scanned_status :
                    continue

                # 判断是否是二级域名，
                if url.count('.') >= 2:
                    is_subdomain = True
                    for suffix in [".com.cn", ".edu.cn", ".net.cn", ".org.cn", ".co.jp",".gov.cn", ".co.uk", "ac.cn",]:
                        if suffix in url :
                            is_subdomain = False
                            break

                    # 二级域名的话跳过，不再爆破三级域名
                    if is_subdomain :
                        yield url_parse(url).get_http_url()
                        continue

                # 域名当作url先扫描
                yield url_parse(url).get_http_url()

                # 遍历子域名并扫描
                domains_list = OneForAll(url).scan()
                domains_list = sorted(set(domains_list), key=domains_list.index)  # 去重 保持顺序
                for domains in domains_list:
                    http_url = url_parse(domains).get_http_url()  #
                    yield http_url
                    continue

    def init_report(self):
        from .setting import TEMPLATE_FILE
        from .setting import TOOLS_REPORT_FILE

        if not os.path.exists(TOOLS_REPORT_FILE):
            with open(TOOLS_REPORT_FILE, 'w+') as w:
                with open(TEMPLATE_FILE, 'r') as r:
                    w.write(r.read())

    def restore(self):
        main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
        restore_path = os.path.join(main_path,'.restore')
        if not os.path.exists(restore_path):
            exit('not found .restore file')

        with open(restore_path,'r') as f: # 判断域名情况
            url = f.read()
            return url


