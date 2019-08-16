#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request,send_from_directory
from flask_mysqldb import MySQL
import hashlib
from base64 import b64encode
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'acq'
mysql = MySQL(app)


## create table login_credentials(email varchar(50) primary key not null, password varchar(32) not null)
## create table user_profile(email varchar(50) primary key not null, username varchar(50), photo mediumblob)

class Post:
    text = ''
    image = NotImplemented



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
    if len(result) != 0:
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
        uploadedImage = request.files['profilePhoto']
        imageBytes = uploadedImage.read()
        # filestream = file.stream
        # readvalue = filestream.read()

        cur = mysql.connection.cursor()
        cur.execute('insert into login_credentials values(%s, %s)', [email, passwordhash])
        mysql.connection.commit()
        
        if imageBytes != '': #needs to be checked
            image = b64encode(imageBytes).decode('utf-8')
            cur.execute('insert into user_profile values(%s, %s, %s)', [email, username, image]) #obj or image?
            mysql.connection.commit()

        cur.close()
    return render_template('profile.html',image=image)



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



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    image = request.files['data']
    return image



if __name__ == '__main__':
    app.run()