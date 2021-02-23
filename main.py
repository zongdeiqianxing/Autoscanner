import os,stat
import time
from lib.arguments_parse import ArgumentParser
from lib.controller import Controller
from lib.setting import TOOLS_DIR


def main():

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