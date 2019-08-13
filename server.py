#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request,send_from_directory
from flask_mysqldb import MySQL
import hashlib
from werkzeug import secure_filename
import os
import requests
from base64 import b64encode
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'acq'
mysql = MySQL(app)
content_type = 'image/jpeg'
headers = {'content-type': content_type}

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
        # photo = getImageLocation()
        # with open(photo, 'rb') as file:
        #     binaryphoto = file.read()
        file = request.files['profilePhoto']
        obj = file.read()
        # filePath = request.form['profilePhotoPath']
        # print("BRO:" + filePath)
        # print("file:", type(file), file, file.filename)
        filestream = file.stream
        # print(file.mimetype)
        readvalue = filestream.read()
        # print(type(readvalue))
        print(type(file))
        # outputfile = open('static/img/test1.png', 'wb')
        # outputfile.write(readvalue)
        print(readvalue)

        image = b64encode(obj).decode("utf-8")
        # print("BRUH",image)
        # print(type(readvalue))
        # if file:
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config[filePath], filename))
        #     return send_from_directory(app.config[filePath],filename)

        # with open(filePath, 'rb') as file:
        #     binaryphoto = file.read()

        # cur = mysql.connection.cursor()
        # cur.execute('insert into login_credentials values(%s, %s)', [email, passwordhash])
        # cur.execute('insert into user_profile values(%s, %s, %s)', [email, username, binaryphoto])        
        # mysql.connection.commit()
        
        #####create table user_profile ( email varchar(50), username varchar(50), photo blob);
        # cur.execute('insert into user_profile values(%s, %s, %s)', [email, username, binaryphoto])
        # mysql.connection.commit()

        # cur.close()
    # response = requests.post('http://127.0.0.1:5000/profile', data=obj, headers=headers)
    # return response
    # return redirect(url_for('profile'))
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
    image = request.files["data"]
    print(image)

            # return redirect(request.url)
    # return render_template("public/upload_image.html")
    return image

if __name__ == '__main__':
    app.run()
