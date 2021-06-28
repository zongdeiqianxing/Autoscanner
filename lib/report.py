import html
import os
import sqlite3
from bs4 import BeautifulSoup
from lib.Tools import Snapshot


main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
REPORT_PATH = os.path.join(main_path, 'report')
REPORT_TEMPLATE = os.path.join(main_path, "lib/template.html")

REPORT_TAB = '''	
    <h3 class="box">{DOMAIN}</h3>
        <div class="tab">
            {IMG_TAB}
            <div class="container">
                <div class="main">
                    <ul class="cbp_tmtimeline">
                    {LI}
                    </ul>
                </div>
            </div>
        </div>
'''

REPORT_LI = '''
        <li>
            <time class="cbp_tmtime" datetime="2014-10-30 18:30"><span>{TIME1}</span> <span>{TIME2}</span></time>
            <div class="cbp_tmicon cbp_tmicon-phone"></div>
            <div class="cbp_tmlabel">
                <h2>{NAME}</h2>
                <p><pre>{REPORT}</pre></p>
            </div>
        </li>
'''


class Report:
    def __init__(self):
        self.body = ""
        self.report = None
        self.batch_num = None
        self.IMG_TAB = r'<div class="tupian"><img src="img/{}.png"></div>'

    def html_report_single(self):
        with sqlite3.connect(os.path.join(main_path, 'scanned_info.db')) as conn:
            def parse(fetch):
                li = ''
                key = [i[0] for i in fetch.description]
                for row in fetch.fetchall():
                    value = [str(row[_]) for _ in range(len(row))]
                    domain = value[1]
                    self.batch_num = value[-2]
                    time = value[-1].split()
                    time1, time2 = time[0], time[1]
                    # 生成li模块
                    for name, report in zip(key[2:-2], value[2:-2]):
                        li += REPORT_LI.format(TIME1=time1, TIME2=time2, NAME=name, REPORT=html.escape(report))

                    # 返回整个tab模块
                    if domain.startswith('http'):
                        yield REPORT_TAB.format(DOMAIN=domain, IMG_TAB=self.IMG_TAB.format(Snapshot.format_img_name(domain)), LI=li)
                    else:
                        yield REPORT_TAB.format(DOMAIN=domain, IMG_TAB='', LI=li)

            tag = ''

            # 插入时从scanned_info确认是否有port扫描，如有需要先插入port信息
            sql = '''
                    select * from host_info 
                    where batch_num = (select batch_num from scanned_info order by id desc limit 1) 
                    order by id desc limit 1 ;
                '''
            fetch = conn.execute(sql)
            for _ in parse(fetch):
                tag += _

            # 下面的limit 1，1 要删掉1
            # 如果port_info有信息， 那么要插入scanned_info中对应的domain数据在port下面
            if tag:
                sql = '''
                    SELECT * from scanned_info 
                    where batch_num = (select batch_num from host_info order by id desc limit 1) 
                        and domain LIKE '%'||(SELECT domain from host_info order by id desc limit 1)||'%'
                    order by id desc limit 1;
                '''
                for _ in parse(conn.execute(sql)):
                    tag += _
            else:
                sql = '''
                    SELECT * from scanned_info order by id desc limit 1 ;
                                '''
                for _ in parse(conn.execute(sql)):
                    tag += _

        if os.path.exists(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num))):
            soup = BeautifulSoup(self.read(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num))), 'html.parser')
        else:
            soup = BeautifulSoup(self.read(REPORT_TEMPLATE), 'html.parser')

        if soup.h3:
            t = BeautifulSoup(tag, 'html.parser')
            soup.h3.insert_before(t)
            self.write(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num)), str(soup))
        else:
            print('Failed to write to report file ! ')

    '''
    获取单个batch_num， 并输出
    此处未完成，瞎做
    '''
    def html_report_entire(self):
        with sqlite3.connect(os.path.join(main_path, 'scanned_info.db')) as conn:
            self.batch_num = conn.execute('select batch_num from scanned_info order by id desc limit 1;').fetchone()[0]
            sql = 'select * from scanned_info where batch_num = {};'.format(self.batch_num)
            fetch = conn.execute(sql).fetchall()
            for row in fetch:
                print(row)
                title = row[1]
                value = [str(row[_]) for _ in range(len(row)) if row[_] is not None]
                value = '\n'.join(value[2:])
                self.body += '<h3 class="box">{}</h3><div class="tab"><pre>{}</pre></div>\n'.format(title, html.escape(value))

        soup = BeautifulSoup(self.read(REPORT_TEMPLATE), 'html.parser')
        if soup.h3:
            t = BeautifulSoup(self.body, 'html.parser')
            soup.h3.insert_before(t)

        self.write(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num)), str(soup))

    @staticmethod
    def read(file):
        with open(file, 'r') as f:
            return f.read()

    @staticmethod
    def write(file, text):
        with open(file, 'w+') as f:
            f.write(text)

    def test(self):
        with sqlite3.connect(os.path.join(main_path, 'scanned_info.db')) as conn:
            sql = '''select * from scanned_info where batch_num = (
                        select batch_num from scanned_info order by id desc limit 1
                        );'''

            fetch = conn.execute(sql).fetchall()
            for row in fetch:
                v = [str(row[c]) for c in range(len(row)) if row[c] is not None]
                print('\n'.join(v[2:]))


