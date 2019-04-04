# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import os
import random
import markdown2


app = Flask(__name__)
myDatabase = 'bsozluk.db'
app.secret_key = os.urandom(24) #this is for the session
 

#reading is done here
@app.route('/')
def index():
	conn = sqlite3.connect(myDatabase)
	c = conn.cursor()
	c.execute('select * from data')
	result = c.fetchall()
	return render_template('index.html', icerik=result)


#login page
@app.route('/logg') 
def logg():
	if 'user' in session:
		return 'already logged in'
	else:
		return render_template('login.html')


#login
@app.route('/login', methods=['POST'])
def login():
	user = request.form['username']
	password = request.form['password']
	if (user == 'badi' and password == '123456'):
		session['user'] = 'badi'
		#return 'username %s - password %s' % (user, password)
		return redirect(url_for('index'))
	else:
		return 'gtfo'


#create
@app.route('/create', methods=['POST'])
def create():
	if 'user' in session:
		icerik = request.form['icerik']
		baslik = request.form['baslik']
		#baslik = baslik.replace('\n', '<br>')
		tarih = str(datetime.datetime.now())
		tarih = tarih[0:10]
		conn = sqlite3.connect(myDatabase)
		c = conn.cursor()
		c.execute('insert into data(baslik, icerik, tarih) values(?,?,?)', (baslik, icerik, tarih))
		conn.commit()
		#return redirect(url_for('index'))
		return redirect(url_for('read', baslik=baslik))
	else:
		return 'gtfo'


#update
@app.route('/update/<int:entry_id>')
def update(entry_id):
	#take from database
	if 'user' in session:
		conn = sqlite3.connect(myDatabase)
		c = conn.cursor()
		c.execute('select * from data where id = ?', [entry_id])
		result = c.fetchone()
		return render_template('edit.html', icerik=result)
	else:
		return 'gtfo'


#edit
@app.route('/edit', methods=['POST'])
def edit():
	if 'user' in session:
		icerik = request.form['icerik']
		entry_id = request.form['entry_id']
		conn = sqlite3.connect(myDatabase)
		c = conn.cursor()
		c.execute('update data set icerik = ? where id = ?', (icerik, entry_id))
		conn.commit()
		c.execute('select baslik from data where id = ?', [entry_id])
		baslik = c.fetchone()
		#return redirect(url_for('index'))
		return redirect(url_for('read', baslik=baslik[0]))

	else:
		return 'gtfo'

#read
@app.route('/read/<baslik>')
def read(baslik):
	conn = sqlite3.connect(myDatabase)
	c = conn.cursor()
	c.execute('select * from data where baslik = ?', [baslik])
	result = list(c.fetchall())
	result = map(lambda x:list(x), result) #result=[list(x) for x in result]
	for record in result:
		record[2] = record[2].replace('\r\n','<br>')
	return render_template('read.html', data=baslik, icerik=result)
#yukarıda read de list ekledim. list ekledim ki icinde degisiklik yapayim yoksa tuple diyip hata veriyodu - immutable



#read by id
@app.route('/oku', methods=['GET'])
def oku():
	entry_id = request.args.get('id')
	conn = sqlite3.connect(myDatabase)
	c = conn.cursor()
	c.execute('select baslik from data where id = ?', [entry_id])
	baslik = c.fetchone()
	c.execute('select * from data where id = ?', [entry_id])
	result = c.fetchall()
	return render_template('oku.html', icerik=result, data=baslik)


#delete
@app.route('/delete/<int:entry_id>')
def delete(entry_id):
	#connect db
	if 'user' in session:
		conn = sqlite3.connect(myDatabase)
		c = conn.cursor()
		c.execute('select baslik from data where id = ?', [entry_id])
		baslik = c.fetchone()
		c.execute('delete from data where id = ?', [entry_id])
		conn.commit()
		return redirect(url_for('read', baslik=baslik[0])) #cunku fetchone gelince unicode falan geliyorud
	else:
		return 'gtfo'


#tum basliklar
@app.route('/tumu')
def tumu():
	conn = sqlite3.connect(myDatabase)
	c = conn.cursor()
	c.execute('select * from data group by baslik order by tarih desc')
	result = c.fetchall()
	return render_template('tumu.html', icerik=result)



#basit arama
@app.route('/ara', methods=['POST'])
def ara():
	baslik = request.form['arama']
	conn = sqlite3.connect(myDatabase)
	c = conn.cursor()
	c.execute('select * from data where baslik = ?', [baslik])
	baslik_out = baslik
	result = c.fetchall()	
	return render_template('read.html', data=baslik_out, icerik=result)



#rastgele baslik
@app.route('/rastgele')
def rastgele():
	conn = sqlite3.connect(myDatabase)
	c = conn.cursor()
	c.execute('select baslik from data group by baslik order by random()')
	baslik_out = c.fetchone()
	baslik_out = baslik_out[0]
	c.execute('select * from data where baslik = ?', [baslik_out])
	result = c.fetchall()
	return render_template('read.html', data=baslik_out, icerik=result)

#run the program
if __name__ == "__main__":
	app.run(debug=True)