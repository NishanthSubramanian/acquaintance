#!/usr/bin/env python

from flask import Flask, render_template, redirect, url_for, request,send_from_directory,session
from flask_mysqldb import MySQL
import hashlib
from base64 import b64encode
from flask import jsonify 
app = Flask(__name__)
import json
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'acq'
mysql = MySQL(app)


## create table login_credentials(email varchar(50) primary key not null, password varchar(32) not null);
## create table user_profile(email varchar(50) primary key not null, username varchar(50), photo mediumblob);
## create table friend_list(email1 varchar(50), email2 varchar(50));
## create table friend_request(email1 varchar(50), email2 varchar(50));
## create table post(email varchar(50), post_id int, image mediumblob, text varchar(1000), timestamp timestamp, likes int);


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
    return redirect(url_for('login'))
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
            session['email']=email
            return redirect(url_for('news_feed'))
            # return render_template('news_feed.html', email=email) #pass email to identify the user here
        else: #return something that says either email or password is wrong
            return render_template('login.html', email=email)
    return

@app.route('/myProfile')
def myProfile():
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute('select photo, username from user_profile where email=%s', [email])
    result=cur.fetchall()
    cur.close()
    image = result[0][0].decode("utf-8")
    return render_template('myProfile.html',email=email,image=image,username=result[0][1])

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    email = session['email']
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['Username']
        uploadedImage = request.files['profilePhoto']
        imageBytes = uploadedImage.read()
        cur.execute('update user_profile set username=%s where email=%s', [username, email])
        mysql.connection.commit()
        if imageBytes != '':
            image = b64encode(imageBytes).decode('utf-8')
            cur.execute('update user_profile set photo=%s where email=%s', [image, email])
            mysql.connection.commit()
    cur.execute('select photo, username from user_profile where email=%s', [email])
    result=cur.fetchall()
    cur.close()
    image = result[0][0].decode("utf-8")
    # print(image)
    print ("updated")
    return redirect(url_for('myProfile'))

        


@app.route('/profile/<email>')
def profile(email):
    myEmail = session['email']
    print(email,myEmail)
    cur = mysql.connection.cursor()
    cur.execute('select photo, username from user_profile where email=%s', [email])
    result=cur.fetchall()
    cur.execute('select * from friend_request where email1=%s and email2=%s', [email, myEmail])
    request1Status=cur.fetchall()
    cur.execute('select * from friend_request where email1=%s and email2=%s', [myEmail, email])
    request2Status=cur.fetchall()
    cur.execute('select * from friend_list where email1=%s and email2=%s', [email, myEmail])
    friendStatus=cur.fetchall()
    cur.close()
    image = result[0][0].decode("utf-8")
    print(request1Status, request2Status, friendStatus)
    # print(type(len(request1Status)), len(friendStatus))
    return render_template('profile.html',myEmail=myEmail,email=email,image=image,username=result[0][1], request1Status=len(request1Status), request2Status=len(request2Status), friendStatus=len(friendStatus))

@app.route('/send_friend_request', methods=['GET', 'POST'])
def send_friend_request():
    email1=session['email']
    print(email1)
    email2=request.form['email']
    friendStatus=request.form['friendStatus']
    request1Status=request.form['request1Status']
    request2Status=request.form['request2Status']
    print(email1, email2, friendStatus, request1Status, request2Status)
    print(type(int(friendStatus)))
    cur = mysql.connection.cursor()
    # cur.execute('insert into friend_request values(%s, %s)', [email1, email2])
    # mysql.connection.commit()
    if int(request1Status) == 0 and int(friendStatus) == 0 and int(request2Status) == 0:
        cur.execute('insert into friend_request values(%s, %s)', [email1, email2])
        mysql.connection.commit()
    elif int(request1Status) == 1:
        cur.execute('delete from friend_request where email1=%s and email2=%s', [email2, email1])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email1, email2])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email2, email1])
        mysql.connection.commit()
    elif int(request2Status) == 1:
        cur.execute('delete from friend_request where email1=%s and email2=%s', [email1, email2])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email1, email2])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email2, email1])
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('profile', email=email2))
    # return render_template('profile.html', ) TODO



@app.route('/news_feed' )
def news_feed():
    # print("HERE")
    myEmail = session['email']
    print(myEmail)
    posts = []
    cur = mysql.connection.cursor()
    # cur.execute('select user_profile.username, post.image, post.text from user_profile inner join () on')
    cur.execute('select username, image, text from post natural join user_profile where email in (select email2 from friend_list where email1=%s) order by timestamp', [myEmail])
    results = cur.fetchall()
    for post in results:
        temp_post = {}
        temp_post['username'] = post[0]
        temp_post['image'] = post[1].decode('utf-8')
        temp_post['text'] = post[2]
        posts.append(temp_post)
        print("''" + str(temp_post['image'])+"''")
    return render_template('news_feed.html', myEmail=myEmail, posts=posts)

@app.route('/upload_post', methods=['POST','GET'])
def upload_post():
    cur = mysql.connection.cursor()
    print(request.form)
    myEmail = session['email']
    cur.execute('select count(*) from post where email=%s',[myEmail])
    numberOfPosts = cur.fetchall()
    image = request.files['image']
    imageBytes = image.read()
    text = request.form['text']
    cur.execute('select unix_timestamp()')
    current_timestamp = cur.fetchall()
    print(type(current_timestamp[0][0]), type(numberOfPosts[0][0]))
    likes = 0
    if imageBytes != '':
        image64 = b64encode(imageBytes).decode('utf-8')
        cur.execute('insert into post values(%s, %s, %s, %s, %s, %s)', [myEmail, numberOfPosts[0][0] + 1, image64, text, current_timestamp, likes])
        mysql.connection.commit()
    else:
        cur.execute('insert into post values(%s, %d, %s, %s, %d, %d)', [myEmail, numberOfPosts[0][0] + 1, None, text, current_timestamp, likes])
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('news_feed'))


@app.route('/search_profile',methods=['GET','POST'])
def search_profile():
    cur = mysql.connection.cursor()
    cur.execute('select email,username from user_profile')
    results = cur.fetchall()
    cur.close()
    # print(results)
    return jsonify(results)

@app.route('/search_results',methods=['GET','POST'])
def search_results():
    myEmail = session['email']
    print(myEmail)
    username=request.form['username']
    cur = mysql.connection.cursor()
    cur.execute('select email,username,photo from user_profile where username=%s',[username])
    results = cur.fetchall()
    cur.close()
    # print(results)
    # displayed = json.dumps(results)
    user_list = []
    for user in results:
        profile = {}
        profile['email'] = user[0]
        profile['username'] = user[1]
        profile['photo'] = user[2].decode("utf-8")
        user_list.append(profile)
    # print(type(results))
    return render_template('display_profiles.html',myEmail = myEmail, profiles=user_list)

if __name__ == '__main__':
    
    app.secret_key = 'acquaintance'
    app.run(debug=True)