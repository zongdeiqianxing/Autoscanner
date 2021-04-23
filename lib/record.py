import sqlite3

class Record():
    def __init__(self):
        self.conn = sqlite3.connect('test.db')
        print("Opened database successfully")
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS RECORD 
               (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
               DOMAIN           TEXT    NOT NULL,
               SCANNED      INT     NOT NULL);''')

    def __enter__(self):
        return self.c

    def __exit__(self, exc_type, exc_val, exc_tb):
        #c.execute('insert into RECORD values(NULL,"http：//testphp.vulnweb.com",1)')
        self.conn.commit()
        self.conn.close()