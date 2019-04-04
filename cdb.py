import sqlite3

conn = sqlite3.connect('bsozluk.db')
c = conn.cursor()
c.execute('create table data(ID INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, icerik TEXT, tarih TEXT)')	
conn.commit()