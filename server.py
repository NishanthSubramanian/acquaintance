#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'acq'
mysql = MySQL(app)


@app.route('/news_feed')
def news_feed():
    return render_template('news_feed.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/')
def identify():
    return render_template('identify.html')

@app.route('/check_user', methods=['GET', 'POST'])
def check_user():
    email = request.form['email']
    cur = mysql.connection.cursor()
    cur.execute('select * from login_credentials where email=%s', [email])
    result = cur.fetchall()
    cur.close()
    if result != "":
        return render_template('login.html', email=email)
    return render_template('signup.html', email=email)


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        passwordhash = hashlib.md5(password.encode()).hexdigest()
        username = request.form['username']
        #no school
        cur = mysql.connection.cursor()
        cur.execute('insert into login_credentials values(%s, %s)', [email, passwordhash])
        mysql.connection.commit()
        #update in profile table too
        cur.close()
    return render_template('news_feed.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/verify_user', methods=['GET', 'POST'])
def verify_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        passwordhash = hashlib.md5(password.encode()).hexdigest()
        cur = mysql.connection.cursor()
        cur.execute('select * from login_credentials where email=%s', [email])
        result = cur.fetchall() #fetch all entries which satisfied the query
        cur.close()
        dbpassword = result[0][1]
        if passwordhash == dbpassword:
            return render_template('news_feed.html', email=email) #pass email to identify the user here
        else: #return something that says either email or password is wrong
            return render_template('login.html', email=email)
    return


if __name__ == '__main__':
    app.run()
