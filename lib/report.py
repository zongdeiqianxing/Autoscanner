import sqlite3
import os
import re
import html
from .Tools import now_time
from lib.urlParser import Parse

# 自一层tab、一层tab内容标签找到分段符，然后截取前文拼接中间的内容形成新报告文件
first_segment = '<!-- insert first tab -->'
first_content_segment = '<!-- insert first content -->'
second_segment = '<!-- insert second_tab_name_template -->'
second_content_segment = '<!-- insert second_tab_content-->'

# 各个应插入的小段的模板，生成时应自底往上，先从第三层开始生成，生成后在第二层的tab标签页里替换，最后替换到第一层里
first_tab_template = "<li>{domain_name}</li>"
first_content_template = '<div class="layui-tab-item">{content}</div>'

# second_tab_template 替换里面tab名和内容后 放到first_content_template中即可
second_tab_template = '''
<div class="layui-tab-item">
      <div class="layui-tab layui-tab-brief" lay-filter="demo" lay-allowclose="true">
        <ul class="layui-tab-title">
          <!-- <li>网站设置</li> -->
          <!-- insert second_tab_name_template -->
        </ul>
        <div class="layui-tab-content">
            <!-- <div class="layui-tab-item">内容2</div> -->
            <!-- insert second_tab_content -->
        </div>
      </div>
'''
second_tab_name_template = "<li>{url_with_port}</li>"
second_tab_conten_template = '<div class="layui-tab-item">{url_with_port}</div>'
thirty_template = '''  
          <fieldset class="layui-elem-field layui-field-title" style="margin-top: 32px;">
              <legend>{tool_name}</legend>
            </fieldset>
            <pre class="layui-code" >
{tool_content}
          </pre>
          '''


main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
REPORT_PATH = os.path.join(main_path, 'report')


class Report:
    def __init__(self):
        self.batch_num = now_time
        self.domain = ''
        self.url_with_port = ''
        self.current_is_host = 0

    def update_report(self, target):
        with sqlite3.connect(os.path.join('scanned_info.db')) as conn:
            def sql_parse(fetch):
                thirty_contents = ''
                key = [i[0] for i in fetch.description]
                for row in fetch.fetchall():
                    value = [str(row[_]) for _ in range(len(row))]
                    if value[1]:
                        if ':' in value[1]:
                            self.url_with_port = value[1]
                        else:
                            self.domain = value[1]
                    # self.batch_num = value[-2]
                    # 生成li模块
                    for name, report in zip(key[2:-2], value[2:-2]):
                        thirty_contents += thirty_template.format(tool_name=name, tool_content=html.escape(report))
                # print(thirty_contents)
                yield thirty_contents

            # host扫描报告，三层
            def thirty_host_part():
                self.current_is_host = 1
                s = ''
                sql = '''select * from host_info where batch_num = {batch_num} and domain = '{domain}';'''.format(
                    batch_num=self.batch_num, domain=target.data['domain'])
                # 添加thirty层
                for _ in sql_parse(conn.execute(sql)):
                    s += _
                return s

            # host扫描报告，三层
            def thirty_web_part(num=0):
                # 先插入web部分的img
                img = './img/{}.png'.format(str(self.url_with_port).lstrip('http://').replace(':', '_'))
                img_insert = '<img src="{}" alt="" width="800px" height="400px">'.format(img)
                s = thirty_template.format(tool_name='Snapshot', tool_content=img_insert)

                sql = '''select * from scanned_info where batch_num = {batch_num} and domain like '%{domain}%' limit {num},1;'''.format(
                    batch_num=self.batch_num, domain=target.data['domain'], num=num)
                # 添加thirty层
                for _ in sql_parse(conn.execute(sql)):
                    s += _
                return s

            def merge_thirty_to_second(template, name, _thirty):
                if self.current_is_host == 1:
                    self.url_with_port = self.domain
                    self.current_is_host = 0

                s2 = template.split('<!-- insert second_tab_name_template -->')[0] + \
                     second_tab_name_template.format(url_with_port=name) + \
                     '<!-- insert second_tab_name_template -->' + \
                     template.split('<!-- insert second_tab_name_template -->')[1].split(
                         '<!-- insert second_tab_content -->')[0] + \
                     first_content_template.format(content=_thirty) + \
                     '<!-- insert second_tab_content -->' + \
                     template.split('<!-- insert second_tab_content -->')[1]

                s2 = re.sub('<!-- <div class="layui-tab-item">内容2</div> -->\s+?<div class="layui-tab-item">',
                            '<div class="layui-tab-item layui-show">', s2)
                return s2

            def merge_second_to_first(_second):
                template = ''
                if os.path.exists(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num))):
                    with open(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num)), 'r', encoding='utf8') as f:
                        template = f.read()
                else:
                    with open(os.path.join(main_path, 'static/template/template.html'), 'r', encoding='utf8') as f:
                        template = f.read()

                s1 = template.split('<!-- insert first tab -->')[0] + \
                     first_tab_template.format(domain_name=self.domain) + \
                     '<!-- insert first tab -->' + \
                     template.split('<!-- insert first tab -->')[1].split('<!-- insert first content -->')[0] + \
                     first_content_template.format(content=_second) + \
                     '<!-- insert first content -->' + \
                     template.split('<!-- insert first content -->')[1]
                return s1

            # host部分的三层就这样
            # 先添加host部分，三层, 并合并到二层
            thirty = thirty_host_part()
            second_tab = merge_thirty_to_second(second_tab_template, self.domain, thirty)  # 下方需要此处为整体模板
            # print(second_tab)

            # 再添加web扫描部分
            # 判断该域名web扫描的条数是否是1条，避免域名多端口是web服务时，报告中重复插入host扫描报告
            sql = "SELECT count(*) from scanned_info where batch_num = {batch_num} and domain LIKE '%{domain}%';".format(
                batch_num=self.batch_num, domain=target.data['domain'])
            url_count = conn.execute(sql).fetchone()[0]
            if url_count < 2:
                thirty = thirty_web_part()
                second_tab = merge_thirty_to_second(second_tab, str(self.url_with_port).replace('http://', ''), thirty)  # 此处理解为不是添加，而是直接替换
            else:
                for num in range(0, url_count, ):
                    thirty = thirty_web_part(num)
                    second_tab = merge_thirty_to_second(second_tab, str(self.url_with_port).replace('http://', ''), thirty)

            # print(second_tab)

            # 添加一层
            s1 = merge_second_to_first(second_tab)
            s1 = re.sub('<div class="layui-tab-item">\s+?<div class="layui-tab-item">',
                        '<div class="layui-tab-item  layui-show">', s1)
            # print(s1)

            with open(os.path.join(REPORT_PATH, '{}-tools.html'.format(self.batch_num)), 'w', encoding='utf8') as f1:
                f1.write(s1)

