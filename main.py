import os
from lib.arguments_parse import ArgumentParser
from lib.controller import Controller
from lib.db import db_init
from lib.download_tools import Download


class AutoScanner:
    def __init__(self):
        for path in ['log', 'tools', 'report', 'report/img']:
            if not os.path.exists(path):
                os.mkdir(path)

        # 需要安装系列工具到tools目录
        # 定义是自动下载，但是由于github问题可能经常会出错；出错的话手动下载解压最好；
        Download().threads_run()

        # if os.path.exists('nuclei-templates'):
        #     os.system('cp -r nuclei-templates /root/nuclei-templates')

        db_init()
        arguments = ArgumentParser()
        controller = Controller(arguments)
        controller.assign_task()


if __name__ == "__main__":
    AutoScanner()