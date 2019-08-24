#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request,send_from_directory
from flask_mysqldb import MySQL
import hashlib
from base64 import b64encode
from flask import jsonify 
app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'acq'
mysql = MySQL(app)


## create table login_credentials(email varchar(50) primary key not null, password varchar(32) not null);
## create table user_profile(email varchar(50) primary key not null, username varchar(50), photo mediumblob);
## create table friend_list(email1 varchar(50), email2 varchar(50));
## create table friend_request(email1 varchar(50), email2 varchar(50));
## create table posts(email varchar(50), text varchar(1000), image mediumblob);

"""
searching for someone would be:
    select * from user_profile where username=searchname;

getting posts in news feed would be:
    select email2 from friend_list where email1=currentemail;
    select post from posts where email in email2 (iterate over entire list of email2)
or we should probably join the tables and then choose

checking for friend requests would be:
    select email1 from friend_request where email2=currentemail;
"""

class Post:
    text = ''
    image = NotImplemented



@app.route('/send_friend_request')
def chat():
    return "Send friend reqeust here"



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
    return redirect(url_for('profile', email=email))
    # return render_template('profile.html',image=image)



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



@app.route('/profile/<email>')
def profile(email):
    print("BROOOOO" + email)
    cur = mysql.connection.cursor()
    cur.execute('select photo, username from user_profile where email=%s', [email])
    result=cur.fetchall()
    cur.close()
    # print("START" + result[0][0])
    image = result[0][0].decode("utf-8")
    return render_template('profile.html',email=email,image=image,username=result[0][1])




@app.route('/news_feed/<string:email>' )
def news_feed(email):
    return render_template('news_feed.html', email=email)

@app.route('/search_profile',methods=['GET','POST'])
def search_profile():
    cur = mysql.connection.cursor()
    cur.execute('select email,username from user_profile')
    results = cur.fetchall()
    cur.close()
    # print(results)
    return jsonify(results)



if __name__ == '__main__':
    app.run()