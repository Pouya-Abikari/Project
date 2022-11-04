from flask import Flask, render_template, session, redirect, url_for, request
import sqlite3
import os
from markupsafe import escape
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(16)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=1)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/form')
def form():
	return render_template('signup.html')

@app.route('/message')
def test():
	return render_template('message.html')

@app.route('/signup',methods=['POST'])
def signup():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("INSERT INTO USER(fname,sname,username,password,email,gender,age,hobby1,hobby2,hobby3,phone,colour1,colour2,course1,course2,course3,year,bio)VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (request.form['fname'],request.form['sname'],request.form['un'],request.form['pw'],request.form['email'],request.form['gender'],request.form['age'],request.form['hobby1'],request.form['hobby2'],request.form['hobby3'],request.form['phone'],request.form['colour1'],request.form['colour2'],request.form['course1'],request.form['course2'],request.form['course3'],request.form['year'],request.form['bio']))
    con.commit()
    con.close()
    return 'insert'

@app.route('/create')
def create():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE USER(
                    fname VARCHAR(15) NOT NULL,
                    sname VARCHAR(20) NOT NULL,
                    username VARCHAR(20) NOT NULL PRIMARY KEY,
                    password VARCHAR(20) NOT NULL,
                    email VARCHAR(25) NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    age INT NOT NULL,
                    hobby1 VARCHAR(20) NOT NULL,
                    hobby2 VARCHAR(20) NOT NULL,
                    hobby3 VARCHAR(20),
                    phone VARCHAR(15) NOT NULL,
                    colour1 VARCHAR(10) NOT NULL,
                    colour2 VARCHAR(10),
                    course1 VARCHAR(20) NOT NULL,
                    course2 VARCHAR(20) NOT NULL,
                    course3 VARCHAR(20) NOT NULL,
                    year INT NOT NULL,
                    bio VARCHAR(150) NOT NULL)
                """)
    return 'created'

@app.route('/msg')
def msg():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE MSG(
                    sec VARCHAR(2) NOT NULL,
                    min VARCHAR(2) NOT NULL,
                    hour VARCHAR(2) NOT NULL,
                    day VARCHAR(2) NOT NULL,
                    month VARCHAR(2) NOT NULL,
                    year VARCHAR(4) NOT NULL,
                    sender VARCHAR(20) NOT NULL,
                    receiver VARCHAR(20) NOT NULL,
                    message VARCHAR(200) NOT NULL)
                """)
    return 'created msg table'

@app.route('/select')
def select():
	con = sqlite3.connect('login.db')
	cur = con.cursor()
	cur.execute("SELECT * FROM USER")
	rows = cur.fetchall()
	return str(rows)

@app.route('/insert', methods=['POST'])
def insert():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("INSERT INTO MSG(sec, min, hour, day, month, year, sender, receiver, message) VALUES (?,?,?,?,?,?,?,?,?)",
                    (request.form['sec'],request.form['min'],request.form['hour'],request.form['day'],request.form['month'],request.form['year'],request.form['sender'],request.form['receiver'],request.form['message']))
    con.commit()
    con.close()
    return 'inserted into MSG'

@app.route('/login', methods=['POST'])
def login():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM USER WHERE Username=? AND Password=?",
    (request.form['un'],request.form['pw']))
    match = len(cur.fetchall())
    if match == 0:
        return "Wrong username and password"
    else:
        session.permanent = True
        session['username'] = request.form['uname']
        return "Welcome " + request.form['uname']

@app.route('/un')
def un():
	if 'username' in session:
		return 'Logged in as %s' % escape(session['username'])
	return 'You are not logged in'

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('un'))

#@app.route("/app")
#def app():
    msg = request.args.get('msg','')
    if msg == '':
        f = open("file.txt", "r")
        return "<form>Message <input name='msg'></form>" + f.read()
    else:
        f = open("file.txt", "a")
        f.write(msg + '<br>')
        f.close()
        f = open("file.txt", "r")
        return "<form>Message <input name='msg'></form>" + f.read()

