import os
import threading
import time
from pathlib import Path
from loguru import logger


# 下方脚本只支持zip格式
Tools = {
    'xray_linux_amd64': "https://download.xray.cool/xray/1.7.0/xray_linux_amd64.zip",
    'crawlergo': 'https://github.com/0Kee-Team/crawlergo/releases/download/v0.4.0/crawlergo_linux_amd64.zip',
    'dirsearch': 'https://github.com/maurosoria/dirsearch/archive/v0.4.1.zip',
    'oneforall': 'https://github.com/shmilylty/OneForAll/archive/v0.4.3.zip',
    'zoomeye': 'https://github.com/knownsec/ZoomEye-python/archive/refs/tags/v2.1.1.zip',
}
tools_path = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], 'tools')


class Download:
    def __init__(self):
        self.zipfile = '{}.zip'
        self.threads = []
        self.numbers = [0]*len(Tools)
        logger.info('检查是否已安装工具，如缺少将进行安装; tips: github网速可能不好，如下载频繁失败，建议百度云获取。')

    def threads_run(self):
        os.chdir(tools_path)
        for k, v in Tools.items():
            t = threading.Thread(target=self.down, args=(k, v,))
            t.start()
            self.threads.append(t)
        for t in self.threads:
            t.join()
        os.chdir('../')

    def down(self, k, v):
        while not os.path.exists('{}'.format(k)):
            try:
                logger.info('缺少{}工具，将自动进行安装'.format(k))
                time.sleep(5)
                if os.path.exists(self.zipfile.format(k)):          # 将删除tools目录下存在的zip文件，避免之前下载失败留存的废文件
                    os.remove(self.zipfile.format(k))
                os.system('wget --no-check-certificate {url} -O {zipfile}'.format(url=v, zipfile=self.zipfile.format(k)))
                os.system('unzip {zipfile} -d {dirname}'.format(zipfile=self.zipfile.format(k), dirname=k))

                # zip解压github的包会存在二级文件目录，这个二级目录里还存在大小写等问题。 所以统一将二级目录的文件移上去
                dirs = [dir for dir in os.listdir(k) if not dir.startswith('.')]
                if len(dirs) == 1 and Path(os.path.join(tools_path, k, dirs[0])).is_dir():
                    os.system('mv {}/{}/* {}/'.format(k, dirs[0], k))
            except Exception as e:
                pass


