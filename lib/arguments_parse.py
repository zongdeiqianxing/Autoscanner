from optparse import OptionParser, OptionGroup
from IPy import IP
import os
import time
from .general import *
from lib.scanner.oneforall import OneForAll

class ArgumentParser():
    def __init__(self,):
        self.args = self.parseArguments()
        options = self.parseArguments()

        if options.restore:
            print("restore模式，从上次中断处重新开始扫描中")
            time.sleep(1)

        if options.url:
            self.urlList = [options.url]

        elif options.domain:
            self.urlList = [options.domain]

        elif options.urlsFile:
            self.urlList = get_file_content(options.urlsFile)

        elif options.domainsFile:
            self.urlList = get_file_content(options.domains_file)

        elif options.qccFile:    #企查查的文件
            print("读取qichacha文件并扫描：")
            time.sleep(1)
            self.urlList = read_xls(options.qccFile).domains

        elif options.domainsFileFromQichacha:
            self.urlList = get_domains_from_qichacha_xlsx(options.domainsFileFromQichacha)

        elif options.cidr :
            try:
                self.urlList = [ip for ip in IP(options.cidr)]
            except :
                print("the input cidr is not correct")

        else :
            exit("need a target input")

        print("urlList:",self.urlList)

        self.toolList = []
        if options.tools:
            for tool_name in options.tools.split(','):
                self.toolList.append(tool_name)

    def parseArguments(self):
        usage = "Usage: %prog [-u|--url] target [-e|--extensions] extensions [options]"
        parser = OptionParser(usage, version="hscan v1 ",epilog="By hujiankai")

        # Mandatory arguments
        mandatory = OptionGroup(parser, "Mandatory")
        mandatory.add_option("-u", "--url", help="Target URL", action="store", type="string", dest="url", default=None)
        mandatory.add_option("-d", "--domain", help="Target domain", action="store", type="string", dest="domain", default=None)
        mandatory.add_option("--fu", help="Target URLS from file", action="store", type="string", dest="urlsFile", default=None)
        mandatory.add_option("--fd", help="Target domains from file", action="store", type="string", dest="domainsFile", default=None)
        mandatory.add_option("--fq", help="Target domains from file of qichacha", action="store",type='string',dest="qccFile", default=None)
        mandatory.add_option("--cidr", help="Target cidr", action="store", type="string", dest="cidr", default=None)

        arg = OptionGroup(parser, "arg")
        arg.add_option("-r","--restore",action="store_true",dest="restore",default=False)
        arg.add_option("-f", "--fast", action="store_true", dest="fastscan", default=False,help="url scan only")

        tools = OptionGroup(parser, "tools")
        tools.add_option("-t", "--tools", help="select tools run", action="store", dest="tools", default="dirsearch,")

        parser.add_option_group(mandatory)
        parser.add_option_group(tools)
        options, arguments = parser.parse_args()

        return options
