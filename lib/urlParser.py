from socket import gethostbyname_ex
import socket
from IPy import IP
from urllib.parse import urlparse
from loguru import logger


class Parse:
    def __init__(self, target):
        if target.endswith('/'):    # port_scan中拿http_url拼接端口
            target = target[:-1]

        if self.isIP(target):
            self.data = {
                'ip': target,
                'domain': target,
                'http_url': 'http://' + target,
            }

        else:
            if not target.count('.') > 1:
                target = 'www.' + target

            for suffix in [".com.cn", ".edu.cn", ".net.cn", ".org.cn", ".gov.cn"]:
                if suffix in target:
                    if not target.count('.') > 2:
                        target = 'www.' + target

            if not target.startswith('http'):
                target = 'http://' + target

            netloc = urlparse(target).netloc
            if ':' in netloc:
                netloc = netloc.split(':')[0]

            if self.isIP(netloc):
                self.data = {
                    'ip': netloc,
                    'domain': netloc,
                    'http_url': target,
                }
            else:
                try:
                    data = list(gethostbyname_ex(netloc))
                    self.data = {'ip': data[2][0],
                                 'domain': netloc,
                                 'http_url': target,
                    }
                #except socket.gaierror as e:
                except Exception as e:
                    logger.error(e)
                    self.data = None

    @staticmethod
    def isIP(str):
        try:
            IP(str)
        except ValueError:
            return False
        return True