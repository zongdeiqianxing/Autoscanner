import os,stat
import time
from lib.arguments_parse import ArgumentParser
from lib.controller import Controller
from lib.setting import TOOLS_DIR


def main():
    '''
    需要安装'crawlergo','dirsearch','oneforall','xray_linux_amd64'到tools目录
    定义是自动下载，但是由于github问题可能经常会出错；出错的话手动下载解压最好；
    具体链接在download_tools.py里有
    '''
    if not os.path.exists(os.path.join(TOOLS_DIR,'install.lock')):
        print('tools not exists; downloading ...')
        time.sleep(3)
        from lib.download_tools import download
        download()

    arguments = ArgumentParser()
    controller = Controller(arguments)
    controller.assign_task()

if __name__ == "__main__":
    main()