import os
import time
import threading
import re
from ..setting import XRAY_REPORT_FILE,TOOLS_DIR

class Xray():
    def __init__(self):
        self.LOG = "/tmp/xray.log"
        self.PROXY = '127.0.0.1:7777'
        self.vuln_scaned = 0

        self.kill_previous_xray_process()
        self.clear_previous_xray_log()

    def scan(self):
        t = threading.Thread(target=self.xray_run, daemon=True)
        t.start()

        ##阻塞模式，因为之前实测后面工具扫描时导致xray请求一片红，
        # while(True):
        #     if self.check_xray_status():
        #         os.system("rm /tmp/xray.log")
        #         self.xray_scan_over = 1
        #         break

    def xray_run(self):
        run_command = "{0}/xray_linux_amd64 webscan --listen {1} --html-output {2} | tee -a {3}".format(TOOLS_DIR,self.PROXY,XRAY_REPORT_FILE,self.LOG)
        print("xray command : ",run_command)
        os.system(run_command)


    def check_xray_status(self):
        cmd = "wc " + self.LOG +"| awk '{print $1}'"
        rows0 = os.popen(cmd).read()
        time.sleep(5)
        rows1 = os.popen(cmd).read()
        cmd = "tail -n 10 {}".format(self.LOG)
        s = os.popen(cmd).read()
        if self.vuln_scaned == 1:
            if rows0 == rows1 and "All pending requests have been scanned" in s:
                print("rows:", rows0, rows1)
                return True
            else:
                return False
        else:
            if rows0 == rows1:
                return True
            else:
                return False

    def clear_previous_xray_log(self):
        if os.path.exists(self.LOG):
            os.system("rm -f {}".format(self.LOG))

    def kill_previous_xray_process(self):
        port = self.PROXY.rsplit(':')[-1]
        process_status = os.popen("netstat -pantu | grep " + port).read()
        if process_status:
            process_num = re.findall("\d{1,}/xray", process_status)
            if process_num:
                process_num = ''.join(process_num)[:-5]
                print(port," port exist previous xray process , killing")
                os.system("kill " + str(process_num))

if __name__ == "__main__":
    A = Xray()