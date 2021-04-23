from .general import url_parse
from .setting import TOOLS_REPORT_FILE
from bs4 import BeautifulSoup
import html

class Report():
    def __init__(self,target):         # all tools use http_url already 
        self.target = url_parse(target).get_netloc()
        self.separate = "\n"*6

    def report_insert(self,tool_log_file,title="",is_file=True):
        soup = BeautifulSoup(self.read(TOOLS_REPORT_FILE),'html.parser')
        if is_file == True:
            report = self.read(tool_log_file)
        else :
            report = tool_log_file
        report = title + '\n' + report

        if not soup.h3 or self.target not in soup.h3.string:
            text = '<h3 class="box">{}</h3><div class="tab"><pre>{}</pre></div>\n'.format(self.target,html.escape(report))
            t = BeautifulSoup(text,'html.parser')
            soup.h3.insert_before(t)
        else:
             soup.div.pre.string += self.separate + report

        self.rewrite_template(str(soup))

    def rewrite_template(self,text):
        with open(TOOLS_REPORT_FILE,'w') as f:
            f.write(text)

    def read(self,file):
        with open(file,'r') as f:
            return f.read()

if __name__ == "__main__":
    X = Report("http://a.testphp.vulnweb.com:9000/index.php")
    X.insert("setting.py")
