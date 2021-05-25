from lib.setting import now_time
from lib.general import path_build
import sqlite3

class db():
    def __init__(self,sql, value=None, dbfile='scanned_info.db'):
        self.db_path = path_build(dbfile)
        self.sql = sql
        self.value = self.replace_date(value)
        self.date = now_time.replace('-','')
        self.db = sqlite3.connect(self.db_path)
        self.c = self.db.cursor()


    def __enter__(self):
        def run():
            if self.value:
                return self.c.execute(self.sql,self.value)
            else:
                return self.c.execute(self.sql)

        try:
            run()
        except sqlite3.OperationalError as e:
            try :
                if 'no such table' in str(e):
                    # target table
                    self.c.execute('''
                        create table if not exists target_info (
                        id INTEGER PRIMARY KEY,input_target text, found_domains text, date integer)''')
                    # scanned info
                    self.c.execute('''
                        create table if not exists scanned_info (
                        id INTEGER PRIMARY KEY,domain text, date integer, crawlergo text, dirsearch text
                        )''')
                run()
            except Exception as e:
                print(e)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.commit()
        self.db.close()


    def replace_date(self,value):
        if 'date' in value:
            v = list(value)
            index = v.index('date')
            v[index] = now_time
            return  tuple(v)