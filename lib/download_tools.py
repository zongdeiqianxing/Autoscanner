import os
from lib.setting import TOOLS_DIR

def download():
    tools = {
    'xray' : "https://download.xray.cool/xray/1.7.0/xray_linux_amd64.zip?download=true",
    'crawlergo' : 'https://github.com/0Kee-Team/crawlergo/releases/download/v0.4.0/crawlergo_linux_amd64.zip',
    'dirsearch' : 'https://github.com/maurosoria/dirsearch/archive/v0.4.0.zip',
    'oneforall' :  'https://github.com/shmilylty/OneForAll/archive/v0.4.3.zip',
    }

    os.chdir(TOOLS_DIR)

    #download
    for key,value in tools.items():
        if key == 'xray' and not value.endswith('.zip'):
            name = 'xray_linux_amd64.zip'
            os.system('wget --no-check-certificate {url} -O {name}'.format(url=value,name=name))

        else:
            #os.system('wget --no-check-certificate {url}'.format(url=value))
            os.system('wget --no-check-certificate {url}'.format(url=value))

    #extract
    os.system('unzip "*.zip"')

    #rename dirsearch and oneforall dir
    dirs = os.listdir(TOOLS_DIR)
    for dir in dirs:
        if dir.lower().startswith('dirsearch'):
            os.system('mv {} dirsearch'.format(dir))

        if dir.lower().startswith('oneforall'):
            os.system('mv {} oneforall'.format(dir))


    tool_name = ['crawlergo','dirsearch','oneforall','xray_linux_amd64']
    if set(tool_name) < set(os.listdir()):
        os.system('touch install.lock')