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
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/verifylogin', methods=['GET', 'POST'])
def verifylogin():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        email = request.form['email']
        password = request.form['pass']
        passwordhash = hashlib.md5(password)
        cur.execute('select * from login_credentials')
        db = cur.fetchall() #fetch all entries which satisfied the query
        cur.close()
        emailexists = 0
        for entry in db:
            for dbemail, dbpassword in entry:
                if email == dbemail: #if email is already registered
                    emailexists = 1
                    if password == dbpassword:
                        return render_template('news_feed.html') #pass email to identify the user here
        if emailexists == 0: #lead to signup page if email is not registered
            return render_template('signup.html', email=request.form['email'])
        else: #return something that says either email or password is wrong
            return 
    return


if __name__ == '__main__':
    app.run()
