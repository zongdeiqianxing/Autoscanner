import re
import os
from lib.report import Report
from lib.general import Run

class Nmap(Report):
    def __init__(self,target,ports_scan=[]):
        super().__init__(target)
        self.LOG_FILE = "/tmp/nmap.log"
        self.target = target
        self.ports_scan = ports_scan
        self.http_open_ports = self.scan()


    def scan(self):
        if not self.ports_scan:
            command = "nmap -sS -Pn -A -v {0} -oN {1}".format(self.target,self.LOG_FILE)
        else:
            command = "nmap -sS -Pn -A -p {0} {1} -v -oN {2}".format(",".join(self.ports_scan),self.target,self.LOG_FILE)

        with Run(command,self.LOG_FILE,) as f:
            self.report_insert(self.LOG_FILE,"NMAP report:")
            return self.get_http_ports(f)

    def get_http_ports(self,text):
        http_ports = re.findall('\d{1,5}/tcp\s{1,}open\s{1,}[ssl/]*http', text)
        http_ports = [x.split("/")[0] for x in http_ports]

        if '80' in http_ports and '443' in http_ports:
            http_ports.remove("443")

        return http_ports

if __name__ == "__main__":
    X = Nmap("47.98.126.199",["80"])
