import os

TOOLS_DIR = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], 'tools')
TOOLS = {
    'xray': "https://download.xray.cool/xray/1.7.0/xray_linux_amd64.zip",
    'crawlergo': 'https://github.com/0Kee-Team/crawlergo/releases/download/v0.4.0/crawlergo_linux_amd64.zip',
    'dirsearch': 'https://github.com/maurosoria/dirsearch/archive/v0.4.1.zip',
    'oneforall': 'https://github.com/shmilylty/OneForAll/archive/v0.4.3.zip',
    }

# github上下载的工具解压后会变成xxx-master , 需要变更为xxx
RENAME_DIRS = ['dirsearch', 'oneforall']


def download():
    os.chdir(TOOLS_DIR)

    for key, value in TOOLS.items():
        os.system('wget --no-check-certificate {url}'.format(url=value))
    os.system('unzip "*.zip"')

    for name_src in os.listdir(TOOLS_DIR):
        for name_dest in RENAME_DIRS:
            if name_src.lower().startswith(name_dest):
                os.system('mv {} {}'.format(name_src, name_dest))

    # 判断工具清单的文件是否都在目录了
    if set([name for name in TOOLS.keys()]).issubset(set(os.listdir())):
        os.system('touch install.lock')
    else:
        exit('The tool has not been downloaded completely, check lib//download_tools.py for details')
