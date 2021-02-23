import os
import time
from lib.general import url_parse,get_ip_from_url
from lib.record import Record
from lib.scanner import xray,crawlergo,nmap,masscan,dirsearch,awvs,request_engine,whatweb

class Controller():
    def __init__(self,arguments):
        self.arguments = arguments
        self.arguments.urlList = sorted(set(self.arguments.urlList), key=self.arguments.urlList.index)  # 去重 保持顺序
        #print(self.arguments.urlList)


    def assign_task(self):
        self.init_report()

        self.xray = xray.Xray()
        self.xray.scan()

        for http_url in self.format_url():
            print("scanning : ",http_url)

            if http_url.count(":") < 2 and http_url.count("/") < 3 : # if like http://a.com:8080 or http://xx.com/1.php ,do self.url_scan()
                ip = get_ip_from_url(http_url)
                if not ip :
                    continue

                open_ports = masscan.Masscan(ip).open_ports
                if not open_ports or len(open_ports) > 20:
                    continue

                http_open_ports = nmap.Nmap(url_parse(http_url).get_netloc(),open_ports).http_open_ports        #use domain not ip in order to report

                if http_open_ports:
                    for port in http_open_ports:
                        http_url_with_port = http_url + ":" + port
                        self.url_scan(http_url_with_port)

                else:
                    print("not found http server port at : ",http_url)
            else:
                self.url_scan(http_url)


    def url_scan(self,target):
        whatweb.Whatweb(target)

        c = crawlergo.Crawlergo(target)
        if not c.sub_domains:                                        #将crawlergo扫描出的子域名添加到任务清单中
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

    def format_url(self):
        for url in self.arguments.urlList:
            http_url = url_parse(url).get_http_url()        #
            yield http_url

    def init_report(self):
        from .setting import TEMPLATE_FILE
        from .setting import TOOLS_REPORT_FILE

        if not os.path.exists(TOOLS_REPORT_FILE):
            with open(TOOLS_REPORT_FILE, 'w+') as w:
                with open(TEMPLATE_FILE, 'r') as r:
                    w.write(r.read())

