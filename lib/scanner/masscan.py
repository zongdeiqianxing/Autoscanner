import os
import re
from ..setting import TOOLS_DIR
from func_timeout import func_set_timeout
import func_timeout


class Masscan():
    def __init__(self,target):
        self.target = target

        try:
            self.open_ports = self.scan()
        except func_timeout.exceptions.FunctionTimedOut:
            self.open_ports = []

    @func_set_timeout(300)
    def scan(self):
        try:
            print("masscan scanning :", self.target)
            #os.system("masscan --ports 0-65535 {0} --rate=10000 -oX {}/masscan.log".format(self.target,self.report_dir))
            result = os.popen("masscan --ports 0-65535 {0} -sS -Pn --rate=1000".format(self.target)).read()
            open_ports = self.reg_port(result)
            print("opening ports:",open_ports)
        except Exception as e:
            print(e)

        return open_ports

    def reg_port(self,text):
        #masscan output : Discovered open port 8814/tcp on 192.168.1.225
        pattern = '\d{1,5}/tcp'
        result = re.findall(pattern, text)
        result = [x[:-4] for x in result]
        return result


if __name__ == "__main__":
    X = Masscan("192.168.1.225")