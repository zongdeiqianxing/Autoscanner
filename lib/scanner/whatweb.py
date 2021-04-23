from lib.general import Run
from lib.report import Report

class Whatweb(Report):
    def __init__(self,target):
        super().__init__(target)
        self.target = target
        self.scan()

    def scan(self):
        command = "whatweb --color never {}".format(self.target)
        with Run(command) as f:
            for i in f.split('\n'):
                if i.startswith('http'):
                    #print(i.replace(',','\n'))
                    self.report_insert(i.replace(',','\n'),'WHATWEB SCAN:',is_file=False)


