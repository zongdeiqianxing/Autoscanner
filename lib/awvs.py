import os
#from lib.general import
import json
import requests
import time
from urllib.parse import urljoin
from lib.setting import REPORT_DIR,AWVS_REPORT_FILE
from lib.general import url_parse
requests.packages.urllib3.disable_warnings()

#https://github.com/h4rdy/Acunetix11-API-Documentation
# awvs open 3443 port
class Awvs():
    def __init__(self,target):
        super().__init__()
        self.target = target
        self.report_name = url_parse(self.target).get_report_name()
        self.username = "test@qq.com"
        self.password = "797eef2a7ea0a1989e81f1113c86c229f1572ac0138cfa3b4d457503ebbb46d8"  #Test123...

        self.base_url = "https://127.0.0.1:3443"           #awvs server ip
        self.session = requests.session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0)',
                        'Content-Type': 'application/json; charset=utf8',
                        'X-Auth': "",
                        'cookie': "",}
        self.get_api_key_and_set()          # it will auto login and get X-Auth and cookie value ,then set them in self.headers
        #self.target_id = ""
        self.scan_session_id = ""
        self.scan_id = ""
        self.target_id = ""

        self.scan()

    def scan(self):
        self.target_id = self.add_target()
        self.start_scan()
        self.get_all_scans_to_find_scanid()

        print(time.strftime("%Y-%m-%d-%H-%M-%S-", time.localtime(time.time())),"awvs start scan ")
        while(True):
            time.sleep(5)
            scan_status = self.get_scan_status()
            if scan_status == 'completed':
                break
        print(time.strftime("%Y-%m-%d-%H-%M-%S-", time.localtime(time.time())), "awvs end scan  : ")
        time.sleep(5)

        #{'vulnerabilities': [], 'pagination': {'count': 0, 'cursor_hash':
        self.get_vulnerabilities()

        self.generate_report()
        time.sleep(5)                                   #wait for generate_report
        self.download_report(self.get_reports())

    def add_target(self):
        url = urljoin(self.base_url,'/api/v1/targets')
        data = {'address': self.target,
                'description': self.target,
                'criticality': 10,}

        result = self.post_request(url,data)
        target_id = result["target_id"]
        if target_id:
            self.target_id = target_id
            print("awvs add target :",target_id)

        return target_id

    def start_scan(self):
        url = urljoin(self.base_url,"/api/v1/scans")
        data = {'target_id': self.target_id,
                'profile_id': '11111111-1111-1111-1111-111111111115',
                'schedule': {"disable": False, "start_date": None, "time_sensitive": False},}
        result = self.post_request(url,data)
        #print(result)

    def get_all_scans_to_find_scanid(self):
        # use /api/v1/scans/{target_id} to get single scan status always be error .
        # so use get all scan status to get single scan status
        url = urljoin(self.base_url,"/api/v1/scans")
        result = self.get_request(url)
        print("get_all_scan_status:",result)
        for i in result["scans"]:
            if i["target_id"] == self.target_id:
                self.scan_session_id = i["current_session"]["scan_session_id"]
                self.scan_id = i["scan_id"]
                print("awvs scan_id:",self.scan_id)
                break

        return True

    def get_scan_status(self):
        url = urljoin(self.base_url,"/api/v1/scans/"+self.scan_id)
        try:
            result = self.get_request(url)
            #print("get_scan_status:",result)
            status = result["current_session"]["status"]
        except:
            pass

        return  status

    def get_vulnerabilities(self):
        url = urljoin(self.base_url,"/api/v1/scans/{scan_id}/results/{scan_session_id}/vulnerabilities".format(scan_id=self.scan_id,scan_session_id=self.scan_session_id))
        result = self.get_request(url)
        print(result)

    def generate_report(self):
        url = urljoin(self.base_url,'/api/v1/reports')
        #{"template_id":"11111111-1111-1111-1111-111111111111","source":{"list_type":"scans","id_list":["6272bfdd-4c6b-41f3-9bee-05afd3948f17"]}}
        data = {"template_id": "11111111-1111-1111-1111-111111111115",
                "source": {
                     "list_type": "scans",
                     "id_list": [self.scan_id],}
             }

        result = self.post_request(url,data)
        #print(result)

    def get_reports(self):
        #https://127.0.0.1:3443/api/v1/reports?l=20&s=template:desc
        url = urljoin(self.base_url,"/api/v1/reports?l=20&s=template:desc")
        while True:                             #wait for generate report
            try:
                result = self.get_request(url)
                print("reports : " ,result)
                report = result["reports"][0]
                if report["download"][0]:
                    break
            except:
                time.sleep(5)

        html_report = report["download"][0]
        if html_report.endswith(".html"):
            html_report = urljoin(self.base_url,html_report)
            print("html_report:",html_report)

        return html_report

    def download_report(self,url):
        os.system("wget -O {report} {url} --no-check-certificate".format(report=os.path.join(REPORT_DIR,AWVS_REPORT_FILE.format(self.report_name)),url=url))

    def get_xauth(self):
        url = urljoin(self.base_url,"/api/v1/me/login")
        data = {"email":self.username,
                "password":self.password,
                "remember_me":'false',
                "logout_previous": 'true',}

        result = self.session.post(url=url,headers=self.headers,data=json.dumps(data),verify=False)
        if result.status_code == 204:
            XAuth = result.headers["X-Auth"]
            #print("awvs login success, X-Auth : ",XAuth)
        else:
            print("awvs login error")

        return XAuth

    def get_api_key_and_set(self):
        XAuth = self.get_xauth()
        self.headers["cookie"] = "ui_session=" + XAuth
        self.headers["X-Auth"] = XAuth

        url = urljoin(self.base_url,'/api/v1/me/credentials/api-key')
        result = self.session.post(url=url,headers=self.headers,data="",verify=False)
        if result.status_code == 200:
            api = json.loads(result.text)
            #print("api_key:",api["api_key"])
            self.headers["X-Auth"] = XAuth
        else:
            print("get api_key error")


    def post_request(self,url,data):
        result = self.session.post(url=url,headers=self.headers,data=json.dumps(data),verify=False)
        result.encoding="utf-8"
        result = result.json()

        return result

    def get_request(self,url):
        result = self.session.get(url=url,headers=self.headers,verify=False)
        result.encoding="utf-8"
        result = result.json()

        return result

if __name__ == "__main__":
    X = Awvs("http://testphp.vulnweb.com")
    #X = Awvs("http://172.16.25.19")