from lib.setting import TOOLS_DIR
from lib.report import Report
from lib.general import Run
import os

class Dirsearch(Report):
    def __init__(self,target):
        super().__init__(target)
        self.LOG = '/tmp/dirsearch.txt'
        self.target = target
        self.urls = []
        self.scan()

    def scan(self):
        command = 'python3 {}/dirsearch/dirsearch.py -e * -x 301,403,404,405,500,501,502,503 -u {} --plain-text-report={}'.format(TOOLS_DIR,self.target,self.LOG)
        with Run(command,self.LOG,delete_file=False) as f:
            if os.path.exists(self.LOG):
                self.report_insert(self.LOG,"DIRSEARCH SCAN:",)
                self.parse()
                os.system('rm -f ' + self.LOG)
            else:
                print("dirsearch log file is not exists")

    def parse(self):
        with open(self.LOG,'r') as f:
            for line in f.readlines():
                url = line.split(' ')[-1]
                self.urls.append(url.strip())

if __name__ == "__main__":
    X = Dirsearch("http://testphp.vulnweb.com")