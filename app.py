from flask import Flask, render_template, session, redirect, url_for, request
from flask_socketio import SocketIO, join_room, emit
import sqlite3
import os
from markupsafe import escape
from datetime import timedelta
import random

app = Flask(__name__)
socketio = SocketIO(app)

app.config['SECRET_KEY'] = os.urandom(16)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)

app.config["SESSION_TYPE"] = "filesystem"

@app.route('/')
def home():
    if 'username' in session:
        session.permanent = True
        yes="yes"
        return render_template('index.html', state=yes)
    return render_template('index.html')

@app.route('/form')
def form():
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/compare')
def compare():
    return render_template('form.html')

@app.route('/account')
def account():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("SELECT username FROM USER")
    result = [item[0] for item in cur.fetchall()]
    userName = escape(session['username'])
    return render_template('account.html', userName=userName, search=result)

@app.route('/signup',methods=['POST'])
def signup():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM USER WHERE Username=?" ,[(request.form['un'])])
    match = len(cur.fetchall())
    con.close()
    if match == 0:
        con = sqlite3.connect('login.db')
        cur = con.cursor()
        cur.execute("INSERT INTO USER(fname,sname,username,password,email)VALUES (?,?,?,?,?)",
                        (request.form['fname'],request.form['sname'],request.form['un'],request.form['pw'],request.form['email']))
        con.commit()
        con.close()
        session.permanent = True
        session['username'] = request.form['un']
        session['chat'] = None
        return redirect(url_for('account'))
    else:
        error='Username already exists, choose another username.'
        return render_template('signup.html', error=error)

@app.route('/signupform',methods=['POST'])
def signupform():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("INSERT INTO FORM(gender,age,hobby1,hobby2,hobby3,phone,colour1,colour2,course1,course2,course3,year,bio)VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (request.form['gender'],request.form['age'],request.form['hobby1'],request.form['hobby2'],request.form['hobby3'],request.form['phone'],request.form['colour1'],request.form['colour2'],request.form['course1'],request.form['course2'],request.form['course3'],request.form['year'],request.form['bio']))
    con.commit()
    con.close()
    return render_template('')

@app.route('/create')
def create():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE USER(
                    fname VARCHAR(15) NOT NULL,
                    sname VARCHAR(20) NOT NULL,
                    username VARCHAR(20) NOT NULL PRIMARY KEY,
                    password VARCHAR(20) NOT NULL,
                    email VARCHAR(25) NOT NULL)
                """)
    return 'created'

@app.route('/createform')
def createform():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE FORM(
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
    return 'created form'

@app.route('/createmsg')
def createmsg():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE MSG(
                    sender VARCHAR(20) NOT NULL,
                    receiver VARCHAR(20) NOT NULL,
                    msg VARCHAR(250) NOT NULL)
                """)
    return 'created msg table'

@app.route("/createcontacts")
def createcontacts():
    con = sqlite3.connect("login.db")
    cur = con.cursor()
    try:
        cur.execute(""" CREATE TABLE contacts(
                        user VARCHAR(20) NOT NULL,
	                    contact VARCHAR(20) NOT NULL)
                    """)
    except sqlite3.OperationalError as e:
        return str(e)
    return "table contacts created"


@app.route('/select')
def select():
    if 'username' in session:
        session.permanent = True
        request.form.get['un'] = escape(session['username'])
        con = sqlite3.connect('login.db')
        cur = con.cursor()
        cur.execute("SELECT hobby1, hobby2, hobby3 FROM USER WHERE Username='un' ")
        rows = cur.fetchall()
        return str(rows)

@app.route('/msg', methods=['POST'])
def msg():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("INSERT INTO MSG(sender, receiver, message) VALUES (?,?,?)",(session['username'], request.form['receiver'], request.form['message']))
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
        error='Wrong username and password, try again.'
        return render_template('index.html', error=error)
    else:
        session.permanent = True
        session['username'] = request.form['un']
        session['chat'] = None
        return redirect(url_for('account'))

@app.route('/un')
def un():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/logout')
def logout():
    session.pop('username', None)
    logout="User logged out successfully!"
    return render_template('index.html', logout=logout)

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        con = sqlite3.connect('login.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM USER WHERE username=?",
            (request.form['user'],))
        result = cur.fetchall()
        con.close()
        if len(result) == 0:
            return 'username not recognised'
        else:
            con = sqlite3.connect('login.db')
            cur = con.cursor()
            cur.execute("SELECT * FROM contacts WHERE user=? and contact=?",
                (session['username'],request.form['user']))
            result = cur.fetchall()
            if len(result) == 0:
                cur.execute("INSERT INTO contacts (user, contact) VALUES (?,?)",
                    (session['username'],request.form['user']))
                con.commit()
                return 'contact added'
            else:
                return 'contact exists'

@app.route('/message')
def message():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("SELECT contact FROM contacts WHERE user=?", (session['username'],))
    result = [item[0] for item in cur.fetchall()]
    return render_template('message.html', chat=session['chat'], contacts=result)

@app.route('/send', methods=['POST'])
def send():
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    cur.execute("INSERT INTO MSG (sender, receiver, msg) VALUES (?,?,?)",
    	       		(session['username'],request.form['receiver'],request.form['msg']))
    con.commit()
    return redirect(url_for('message'))

@app.route('/getMsgs', methods=['GET'])
def getMsgs():
    session['chat'] = request.args.get("name")
    con = sqlite3.connect('login.db')
    cur = con.cursor()
    usr = session['username']
    chat = session['chat']
    cur.execute("""SELECT sender, msg FROM MSG WHERE (receiver=? AND sender=?) OR (receiver=? AND sender=?)""", (usr,chat,chat,usr))
    rows = cur.fetchall()
    return rows

@app.route('/createforgot')
def createforgot():
    con = sqlite3.connect("forgot.db")
    cur = con.cursor()
    try:
        cur.execute(""" CREATE TABLE verify(
            verify CHAR(5) NOT NULL)
                    """)
    except sqlite3.OperationalError as e:
        return str(e)
    return "table verify created"

@app.route('/forgot', methods=['POST'])
def forgot():
    verify = (random.randrange(1, 10))
    con = sqlite3.connect('forgot.db')
    cur = con.cursor()
    cur.execute("INSERT INTO USER (verify) VALUES (?)", (verify))
    con.commit()
    return render_template('forgot.html')

@socketio.on('join')
def on_join(data):
    join_room(data['room'])
    emit('chat message', data['msg'], to=data['room'])

