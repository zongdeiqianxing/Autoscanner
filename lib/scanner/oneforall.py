from ..setting import TOOLS_REPORT_FILE
from ..setting import TOOLS_DIR
import os
import csv

class OneForAll():
    def __init__(self,target):
        self.target = target
        
        if os.path.exists(os.path.join(TOOLS_DIR, 'OneForAll')):
            os.system('cp -r {path}/OneForAll/ {path}/oneforall/'.format(path=TOOLS_DIR))

    def scan(self):
        print("Brute domain: " + self.target)

        os.system('python3 {}/OneForAll/oneforall.py --target {} run'.format(TOOLS_DIR, self.target))
        report_file = "{}/OneForAll/results/{}.csv".format(TOOLS_DIR, self.target)
        if not os.path.exists(report_file):
            exit("Not found the OneForAll's output file ")

        return self.get_subdomains(report_file)


    def get_subdomains(self,report_file):
        with open(report_file, 'r') as csvfile:
            csvfile.__next__()
            reader = csv.reader(csvfile)
            column = [row[5] for row in reader]
            urlList = list(set(column))

        return urlList
