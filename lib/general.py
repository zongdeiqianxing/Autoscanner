from urllib.parse import urlparse
import os
import socket
import json
import xlrd


class read_xls:
    def __init__(self, file):
        self.base_str = list('0123456789abcdefghijklmnopqrstuvwxyz.-_')
        self.domains = self.read_xls(file)

    def read_xls(self, file):
        try:
            workbook = xlrd.open_workbook(file)
            sheet1 = workbook.sheet_by_index(0)
            column = sheet1.col_values(3)
            return self.filter(column)
        except Exception as e:
            exit(e)

    def filter(self, domains):
        domains_filterd = []
        for domain in domains:
            if domain is None:
                break
            if ';' in domain:
                domain = domain.split(';')[0]
            # 判断域名内容是否标准，比如是否存在中文
            if not set(list(domain)) < set(self.base_str):
                print('domain {} 不规范，忽略'.format(domain))
                continue
            if not len(domain) < 3:
                domains_filterd.append(domain)
        return sorted(set(domains_filterd), key=domains_filterd.index)

class Run():
    def __init__(self,command,logfile='',delete_file=True):
        self.command = command
        self.logfile = logfile
        self.delete_file = delete_file
        print("scan: ",self.command)

    def __enter__(self):
        try:
            result = os.popen(self.command.format(self.logfile)).read()
            print(result)
            return result

        except Exception as e:
            print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.delete_file and self.logfile and os.path.exists(self.logfile):
            os.system("rm -f " + self.logfile)
        print('end scan')


class url_parse():
    def __init__(self,url):
        self.url = url.strip("/")

    def get_http_url(self):
        if self.url.count(".") == 1:
            if self.url.startswith("http"):
                self.url = self.url.rsplit("/")[0] + '//www.' + self.url.rsplit("/")[-1]        #Avoid examples like http//a.com
            else:
                self.url = "www." + self.url

        if self.url.startswith("http"):
            return self.url
        else:
            return "http://" + self.url

    def get_netloc(self):
        http_url = self.get_http_url()
        return urlparse(http_url).netloc

    def get_report_name(self):
        name = self.get_netloc().replace(":","_")
        return name

def get_ip_from_url(http_url):
    netloc = url_parse(http_url).get_netloc()
    if netloc.count(':') > 0:
        index = netloc.rindex(':')
        netloc = netloc[:index]
        #print(netloc)

    try:
        ip = socket.getaddrinfo(netloc, None)                           # resolve domain to ip from local dns
        return ip[0][4][0]
    except Exception as e:
        print(e,' using aliyun resolve:')

        from lib.scanner.request_engine import Request
        url = 'http://203.107.1.33/100000/d?host={}'.format(netloc)
        try:
            response = Request().repeat(url)
            response = json.loads(response.text)
            ip = response['client_ip']
            return ip
        except Exception as e:
            print(e)
            return None

def get_file_content(file_path):
    if not os.path.exists(file_path):
        exit("not found file:{}".format(file_path))

    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines()]


def dir_is_exists_or_create(*dir_path):
    for path in dir_path:
        if not os.path.exists(path):
            os.mkdir(path)

def file_is_exists_or_create(*file_path):
    for path in file_path:
        if not os.path.exists(path):
            os.mknod(path)

def check_dict_key_vaild(dict,*keys):
    for key in keys:
        if not dict.has_key(key):
            return False
    return True


def path_build(*path):
    main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
    path = os.path.join(main_path, *path)
    return path


def extract_tools_file(tools_dir_path):
    if not os.path.exists(os.path.join(tools_dir_path, 'install.lock')):
        os.system(
            "for zip in {0}/*.zip; do unzip -d {0}/ $zip; done;touch {0}/install.lock".format(tools_dir_path))

if __name__ == "__main__":
    url = "http://a.com:80"
    print(url_parse(url).get_netloc()[:-3])
