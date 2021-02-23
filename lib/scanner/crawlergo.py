#!/usr/bin/python3
# coding: utf-8


import simplejson
import subprocess
import os
from lib.report  import Report
from lib.setting import TOOLS_DIR

class Crawlergo(Report):
    def __init__(self,target):
        super().__init__(target)
        self.BROWERS = '/usr/bin/google-chrome'
        self.XRAY_PROXY = 'http://127.0.0.1:7777'

        self.target = target
        self.scan()

    def scan(self):
        print("crawlergo scanning : ",self.target)

        try:
            crawlergo = os.path.join(TOOLS_DIR,"crawlergo")
            print(1)
            #cmd = [crawlergo, "-c", self.BROWERS, "-t", "5", "-f", "smart", "--push-to-proxy", self.XRAY_PROXY, "--push-pool-max", "10", "--fuzz-path", "-o", "json", self.target]
            cmd = [crawlergo, "-c", self.BROWERS, "--push-to-proxy", self.XRAY_PROXY, "-o", "json", self.target]
            rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(2)
            output, error = rsp.communicate()
            #  "--[Mission Complete]--"  是任务结束的分隔字符s串
            result = simplejson.loads(output.decode().split("--[Mission Complete]--")[1])
            req_list = result["req_list"]
            urls = []
            for req in req_list:
                print("crawlergo found :" , req['url'])
                urls.append(req['url'])
                #self.put_to_file(req['url'],os.path.join(self.report_dir,url_parse(self.target).get_netloc()+"-crawlergo.url"))
            #print(req_list[0])

            #subdomain 在controller模块中已添加进入扫描
            self.sub_domains = result["sub_domain_list"]
            # for domain in sub_domains:
            #     print("sub found :", domain)
                #self.put_to_file(domain, os.path.join(self.report_dir, url_parse(self.target).get_netloc() + "-crawlergo.sub"))


            rows = ["crawlergo urls found:"] + urls + ['\n'*1,"crawlergo subdomains found:"] + self.sub_domains
            self.report_insert('\n'.join(rows),"crawlergo report:",is_file=False)
        except Exception as f:
            print(f)
            pass

    # def put_to_file(self,row,filename):
    #     with open(filename,'a+') as f:
    #         f.write(row)

if __name__ == '__main__':
    A = Crawlergo("http://testphp.vulnweb.com")