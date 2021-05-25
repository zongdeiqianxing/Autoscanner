from lib.general import path_build
from lib.general import dir_is_exists_or_create
import time


# TIME
now_time = time.strftime("%Y-%m-%d-%H-%M-%S-", time.localtime(time.time()))


# DIR PATH
REPORT_DIR = path_build("report")
TOOLS_DIR = path_build("tools")
dir_is_exists_or_create(REPORT_DIR,TOOLS_DIR)

TOOLS_REPORT_NAME = now_time + "tools-scan.html"
TOOLS_REPORT_FILE = path_build('report',TOOLS_REPORT_NAME)

XRAY_REPORT_NAME = now_time + "xray.html"
XRAY_REPORT_FILE = path_build('report',XRAY_REPORT_NAME)

AWVS_REPORT_FILE = now_time + "{}.awvs.html"

TEMPLATE_FILE = path_build('lib','template.html')



