from optparse import OptionParser, OptionGroup
from .general import get_file_content, read_xls
import time


class ArgumentParser:
    def __init__(self,):
        options = self.parse_arguments()
        self.targets = []

        if options.domain:
            self.targets += [options.domain]
        elif options.file:
            self.targets += get_file_content(options.file)
        elif options.qccFile:
            self.targets += read_xls(options.qccFile).domains
        else:
            exit("need a target input")

        self.verbose = options.verbose
        self.mode = ['web_scan', 'ports_scan', 'subdomains_scan'] if options.mode and options.mode == 'all' else []
        if not self.mode and options.mode:
            for _ in options.mode.split(","):
                if _ in ['web_scan', 'ports_scan', 'subdomains_scan'] and _ not in self.mode:
                    self.mode.append(_)

    @staticmethod
    def parse_arguments():
        usage = """
                    _         _       ____
           / \  _   _| |_ ___/ ___|  ___ __ _ _ __  _ __   ___ _ __
          / _ \| | | | __/ _ \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
         / ___ \ |_| | || (_) |__) | (_| (_| | | | | | | |  __/ |
        /_/   \_\__,_|\__\___/____/ \___\__,_|_| |_|_| |_|\___|_|
        Usage: %prog [-u|--url] target [-e|--extensions] extensions [options]"""
        parser = OptionParser(usage, epilog="By hujiankai")

        mandatory = OptionGroup(parser, "Mandatory")
        mandatory.add_option("-d", "--domain", help="Target domain", action="store", type="string", dest="domain")
        mandatory.add_option("-f", help="Target file", action="store", type="string", dest="file", )
        mandatory.add_option("--fq", help="Target domains from qichacha file", action="store", type='string', dest="qccFile",)
        mandatory.add_option("--cidr", help="Target cidr", action="store", type="string", dest="cidr",)

        arg = OptionGroup(parser, "arg")
        arg.add_option("-r", "--restore", action="store_true", dest="restore", default=False)
        arg.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
        arg.add_option('-m', '--mode', help='scan mode. support all, web_scan, ports_scan, subdomains_scan. default: all.', action='store', dest='mode', default='all', metavar='STATUS')

        tools = OptionGroup(parser, "tools")
        tools.add_option("-t", "--tools", help="select tools run", action="store", dest="tools", default=None)

        parser.add_option_group(mandatory)
        parser.add_option_group(arg)
        parser.add_option_group(tools)
        options, arguments = parser.parse_args()

        return options


