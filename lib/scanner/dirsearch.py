from lib.setting import TOOLS_DIR
from lib.report import Report
from lib.general import Run
import os
from func_timeout import func_set_timeout
import func_timeout

class Dirsearch(Report):
    def __init__(self,target):
        super().__init__(target)
        self.LOG = '/tmp/dirsearch.csv'
        self.target = target
        self.urls = []

        try:
            self.scan()
        except func_timeout.exceptions.FunctionTimedOut:
            print('dirsearch timeout')

    @func_set_timeout(300)
    def scan(self):
        command = 'python3 {}/dirsearch/dirsearch.py -e * -x 301,403,404,405,500,501,502,503 -u {} --csv-report {}'.format(TOOLS_DIR,self.target,self.LOG)
        print('dirsearch is running')
        with Run(command,self.LOG,delete_file=False) as f:
            if os.path.exists(self.LOG):
                #print("dirsearch log file exists , and run report_insert")
                print('\n'.join(self.report_parse(self.LOG)))
                self.report_insert('\n'.join(self.report_parse(self.LOG)),"DIRSEARCH SCAN:",is_file=False)
                os.system('rm -f ' + self.LOG)
            else:
                print("dirsearch log file is not exists , may be because of dirsearch cannot connect the {}".format(self.target))

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
                    if not line[1]:
                        continue

                    self.urls.append(line[1])
                    try:
                        s = "{:<}  - {:>5}B  -  {:<5}".format(line[2], line[3], line[1])
                    except:
                        continue
                    rows.append(s)
        return rows

if __name__ == "__main__":
    X = Dirsearch("http://testphp.vulnweb.com")
