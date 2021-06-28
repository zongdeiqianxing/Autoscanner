import os
import time
from lib.arguments_parse import ArgumentParser
from lib.controller import Controller
from lib.db import db_init


def main():
    for dir in ['log', 'tools', 'report', 'report/img']:
        if not os.path.exists(dir):
            os.mkdir(dir)

    '''
    需要安装系列工具到tools目录
    定义是自动下载，但是由于github问题可能经常会出错；出错的话手动下载解压最好；
    具体链接在download_tools.py里有
    '''
    if not os.path.exists('tools/install.lock'):
        print('tools not exists; downloading ...')
        time.sleep(3)
        from lib.download_tools import download
        download()

    db_init()
    arguments = ArgumentParser()
    controller = Controller(arguments.args)
    controller.assign_task()


if __name__ == "__main__":
    main()