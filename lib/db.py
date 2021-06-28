import sqlite3
import os

main_path = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]


'''
初试化表结构
'''
def db_init():
    with sqlite3.connect('scanned_info.db') as conn:
        conn.execute('''
                                create table if not exists target_info (
                                    id INTEGER PRIMARY KEY,
                                    target text, 
                                    oneforall text, 
                                    crawlergo text,
                                    batch_num integer, 
                                    date timestamp not null default (datetime('now','localtime')))
                                    ''')

        conn.execute('''
                                create table if not exists host_info (
                                    id INTEGER PRIMARY KEY,
                                    domain text, 
                                    nslookup text,
                                    iplocation text,
                                    masscan text,
                                    nmap text, 
                                    batch_num integer, 
                                    date timestamp not null default (datetime('now','localtime')))
                                    ''')

        conn.execute('''
                                create table if not exists scanned_info (
                                    id INTEGER PRIMARY KEY,
                                    domain text,
                                    whatweb text,
                                    crawlergo text, 
                                    dirsearch text,
                                    batch_num integer, 
                                    date timestamp not null default (datetime('now','localtime'))
                                )''')


def db_insert(sql, *value):
    with sqlite3.connect(os.path.join(main_path, 'scanned_info.db')) as conn:
        conn.execute(sql, value)  # *value返回(1,) (1,2)这种元祖


def db_update(table, name, text):
    with sqlite3.connect(os.path.join(main_path, 'scanned_info.db')) as conn:
        sql = 'update {table} set {column}=? order by id desc limit 1;'.format(table=table, column=name)
        conn.execute(sql, (text,))