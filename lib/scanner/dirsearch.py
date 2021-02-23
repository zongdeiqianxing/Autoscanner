from lib.setting import TOOLS_DIR
from lib.report import Report
from lib.general import Run
import os

class Dirsearch(Report):
    def __init__(self,target):
        super().__init__(target)
        self.LOG = '/tmp/dirsearch.csv'
        self.target = target
        self.urls = []
        self.scan()

    def scan(self):
        command = 'python3 {}/dirsearch/dirsearch.py -e * -x 301,403,404,405,500,501,502,503 -u {} --csv-report {}'.format(TOOLS_DIR,self.target,self.LOG)
        with Run(command,self.LOG,delete_file=False) as f:
            if os.path.exists(self.LOG):
                print("dirsearch log file exists , and run report_insert")
                print('\n'.join(self.report_parse(self.LOG)))
                self.report_insert('\n'.join(self.report_parse(self.LOG)),"DIRSEARCH SCAN:",is_file=False)
                os.system('rm -f ' + self.LOG)
            else:
                print("dirsearch log file is not exists")

    # 将dirsearch的csv报告重新整理下
    def report_parse(self,log_file):
        rows = []
        with open(log_file,'r') as f:
            try:
                next(f)                     #always raise a StopIteration error before
            except StopIteration as s:
                print(s)
            finally:
                for line in f.readlines():
                    line = line.strip().split(',')
                    self.urls.append(line[1])
                    s = "{:<}  - {:>5}B  -  {:<5}".format(line[2], line[3], line[1])
                    rows.append(s)
        return rows



if __name__ == "__main__":
    X = Dirsearch("http://testphp.vulnweb.com")