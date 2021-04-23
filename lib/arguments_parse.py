from optparse import OptionParser, OptionGroup
from IPy import IP
import os
from .general import *
from lib.scanner.oneforall import OneForAll

class ArgumentParser():
    def __init__(self,):
        options = self.parseArguments()

        if options.url:
            self.urlList = [options.url]

        elif options.domain:
            self.urlList = [options.domain]

        elif options.urlsFile:
            self.urlList = get_file_content(options.urlsFile)

        elif options.domainsFile:
            self.urlList = get_file_content(options.domains_file)

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

        if options.restore:
            self.restore = True
        else :
            self.restore = False

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
        mandatory.add_option("--fdq", help="Target domains from file of qichacha", action="store", type="string", dest="domainsFileFromQichacha",default=None)
        mandatory.add_option("--cidr", help="Target cidr", action="store", type="string", dest="cidr", default=None)

        mandatory.add_option("-r","--restore",action="store_true",dest="restore",help="restore scan")

        tools = OptionGroup(parser, "tools")
        tools.add_option("-t", "--tools", help="select tools run", action="store", dest="tools", default="dirsearch,")

        parser.add_option_group(mandatory)
        parser.add_option_group(tools)
        options, arguments = parser.parse_args()

        return options