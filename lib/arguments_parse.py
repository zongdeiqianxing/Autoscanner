from optparse import OptionParser, OptionGroup
from IPy import IP
from .general import get_file_content, read_xls
import time


class ArgumentParser:
    def __init__(self,):
        self.args = self.parse_arguments()
        urls, domains = [], []

        if self.args.url:
            urls += [self.args.url]
        elif self.args.domain:
            domains += [self.args.domain]
        elif self.args.urlsFile:
            urls += get_file_content(self.args.urlsFile)
        elif self.args.domainsFile:
            domains += get_file_content(self.args.domainsFile)
        elif self.args.qccFile:
            domains += read_xls(self.args.qccFile).domains
        elif self.args.cidr:
            try:
                urls += [ip for ip in IP(self.args.cidr)]
            except Exception as e:
                exit(e)
        else:
            exit("need a target input")

        self.args.urlList, self.args.domainList = urls, domains

    @staticmethod
    def parse_arguments():
        usage = "Usage: %prog [-u|--url] target [-e|--extensions] extensions [options]"
        parser = OptionParser(usage, epilog="By hujiankai")

        mandatory = OptionGroup(parser, "Mandatory")
        mandatory.add_option("-u", "--url", help="Target URL", action="store", type="string", dest="url",)
        mandatory.add_option("-d", "--domain", help="Target domain", action="store", type="string", dest="domain")
        mandatory.add_option("--fu", help="Target URLS from file", action="store", type="string", dest="urlsFile", )
        mandatory.add_option("--fd", help="Target domains from file", action="store", type="string", dest="domainsFile")
        mandatory.add_option("--fq", help="Target domains from qichacha file", action="store", type='string', dest="qccFile",)
        mandatory.add_option("--cidr", help="Target cidr", action="store", type="string", dest="cidr",)

        arg = OptionGroup(parser, "arg")
        arg.add_option("-r", "--restore", action="store_true", dest="restore", default=False)
        arg.add_option("-f", "--fast", action="store_true", dest="fastscan", default=False,help="url scan only")

        tools = OptionGroup(parser, "tools")
        tools.add_option("-t", "--tools", help="select tools run", action="store", dest="tools", default=None)

        parser.add_option_group(mandatory)
        parser.add_option_group(arg)
        parser.add_option_group(tools)
        options, arguments = parser.parse_args()

        return options


