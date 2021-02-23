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
            self.urlList = OneForAll(options.domain).scan()

        elif options.urlsFile:
            self.urlList = get_file_content(options.urls_file)

        elif options.domainsFile:
            self.urlList = self.get_domainsFile_urls(get_file_content(options.domains_file))

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

    def get_domainsFile_urls(self,domains):
        urlList =[]
        for domain in domains:
            urlList += OneForAll(domain).scan()

        return list(set(urlList))

    def parseArguments(self):
        usage = "Usage: %prog [-u|--url] target [-e|--extensions] extensions [options]"
        parser = OptionParser(usage, version="hscan v1 ",epilog="By hujiankai")

        # Mandatory arguments
        mandatory = OptionGroup(parser, "Mandatory")
        mandatory.add_option("-u", "--url", help="Target URL", action="store", type="string", dest="url", default=None)
        mandatory.add_option("-d", "--domain", help="Target domain", action="store", type="string", dest="domain", default=None)
        mandatory.add_option("--fu", help="Target URLS from file", action="store", type="string", dest="urlsFile", default=None)
        mandatory.add_option("--fd", help="Target domains from file", action="store", type="string", dest="domainsFile", default=None)
        mandatory.add_option("--cidr", help="Target cidr", action="store", type="string", dest="cidr", default=None)


        tools = OptionGroup(parser, "tools")
        tools.add_option("-t", "--tools", help="select tools run", action="store", dest="tools", default="dirsearch,")

        parser.add_option_group(mandatory)
        parser.add_option_group(tools)
        options, arguments = parser.parse_args()

        return options