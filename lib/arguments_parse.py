from optparse import OptionParser, OptionGroup
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
        else:
            exit("need a target input")

        self.args.urlList, self.args.domainList = urls, domains
        self.args.verbose = self.args.verbose


    @staticmethod
    def parse_arguments():
        usage = """
                    _         _       ____
           / \  _   _| |_ ___/ ___|  ___ __ _ _ __  _ __   ___ _ __
          / _ \| | | | __/ _ \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
         / ___ \ |_| | || (_) |__) | (_| (_| | | | | | | |  __/ |
        /_/   \_\__,_|\__\___/____/ \___\__,_|_| |_|_| |_|\___|_|
        Usage: %prog [-u|--url] target [-e|--extensions] extensions [options]"""
        parser = OptionParser(usage, epilog="By zongdeiqianxing")

        mandatory = OptionGroup(parser, "Mandatory")
        mandatory.add_option("-u", "--url", help="Target URL", action="store", type="string", dest="url",)
        mandatory.add_option("-d", "--domain", help="Target domain", action="store", type="string", dest="domain")
        mandatory.add_option("--fu", help="Target URLS from file", action="store", type="string", dest="urlsFile", )
        mandatory.add_option("--fd", help="Target domains from file", action="store", type="string", dest="domainsFile")
        mandatory.add_option("--fq", help="Target domains from qichacha file", action="store", type='string', dest="qccFile",)

        arg = OptionGroup(parser, "arg")
        arg.add_option("-r", "--restore", action="store_true", dest="restore", default=False)
        arg.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)

        ex_tools = OptionGroup(parser, "ex-tools")
        ex_tools.add_option("--ex", "--ex_nuclei", help="Nuclei will warn in Tencent Cloud, so you can exclude nuclei", action="store", dest="ex_nuclei", default=False)

        parser.add_option_group(mandatory)
        parser.add_option_group(arg)
        parser.add_option_group(ex_tools)
        options, arguments = parser.parse_args()

        return options


