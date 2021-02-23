from lib.general import path_build
import time

now_time = time.strftime("%Y-%m-%d-%H-%M-%S-", time.localtime(time.time()))


REPORT_DIR = path_build("report")
TOOLS_DIR = path_build("tools")

#要考虑把xray和tools的now——time弄一致还是怎么的
#TOOLS_REPORT_NAME = 'template.html'
TOOLS_REPORT_NAME = now_time + "tools-scan.html"
TOOLS_REPORT_FILE = path_build('report',TOOLS_REPORT_NAME)

XRAY_REPORT_NAME = now_time + "xray.html"
XRAY_REPORT_FILE = path_build('report',XRAY_REPORT_NAME)

AWVS_REPORT_FILE = now_time + "{}.awvs.html"

TEMPLATE_FILE = path_build('lib','template.html')



