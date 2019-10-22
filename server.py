#!/usr/bin/env python

import json
from flask import Flask, render_template, redirect, url_for, request, send_from_directory, session
from flask_mysqldb import MySQL
import hashlib
from base64 import b64encode
from flask import jsonify
from flask_socketio import SocketIO, send, emit
from datetime import datetime

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
## create table post(email varchar(50), post_id int, image mediumblob, text varchar(1000), timestamp bigint, likes int);
## create table likes(poster_email varchar(50), post_id int, liker_email varchar(50));
## create table chat(email1 varchar(50), email2 varchar(50), message varchar(2000), timestamp bigint);
## create table socket(email varchar(50), socket_id varchar(50));


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

socketio = SocketIO(app)
users = {}

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
        cur.execute('insert into login_credentials values(%s, %s)',
                    [email, passwordhash])
        mysql.connection.commit()

        if imageBytes != '':  # needs to be checked
            image = b64encode(imageBytes).decode('utf-8')
            cur.execute('insert into user_profile values(%s, %s, %s)', [
                        email, username, image])  # obj or image?
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
        result = cur.fetchall()  # fetch all entries which satisfied the query
        cur.close()
        dbpassword = result[0][1]
        if passwordhash == dbpassword:
            session['email'] = email
            return redirect(url_for('news_feed'))
            # return render_template('news_feed.html', email=email) #pass email to identify the user here
        else:  # return something that says either email or password is wrong
            return render_template('login.html', email=email)
    return


@app.route('/myProfile')
def myProfile():
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute(
        'select photo, username from user_profile where email=%s', [email])
    result = cur.fetchall()
    cur.close()
    image = result[0][0].decode("utf-8")
    return render_template('myProfile.html', email=email, image=image, username=result[0][1])


@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    email = session['email']
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        username = request.form['Username']
        uploadedImage = request.files['profilePhoto']
        imageBytes = uploadedImage.read()
        cur.execute('update user_profile set username=%s where email=%s', [
                    username, email])
        mysql.connection.commit()
        if imageBytes != '':
            image = b64encode(imageBytes).decode('utf-8')
            cur.execute(
                'update user_profile set photo=%s where email=%s', [image, email])
            mysql.connection.commit()
    cur.execute(
        'select photo, username from user_profile where email=%s', [email])
    result = cur.fetchall()
    cur.close()
    image = result[0][0].decode("utf-8")
    # print(image)
    print("updated")
    return redirect(url_for('myProfile'))


@app.route('/profile/<email>')
def profile(email):
    myEmail = session['email']
    print(email, myEmail)
    cur = mysql.connection.cursor()
    cur.execute(
        'select photo, username from user_profile where email=%s', [email])
    result = cur.fetchall()
    cur.execute(
        'select * from friend_request where email1=%s and email2=%s', [email, myEmail])
    request1Status = cur.fetchall()
    cur.execute(
        'select * from friend_request where email1=%s and email2=%s', [myEmail, email])
    request2Status = cur.fetchall()
    cur.execute(
        'select * from friend_list where email1=%s and email2=%s', [email, myEmail])
    friendStatus = cur.fetchall()
    cur.close()
    image = result[0][0].decode("utf-8")
    print(request1Status, request2Status, friendStatus)
    # print(type(len(request1Status)), len(friendStatus))
    return render_template('profile.html', myEmail=myEmail, email=email, image=image, username=result[0][1], request1Status=len(request1Status), request2Status=len(request2Status), friendStatus=len(friendStatus))


@app.route('/send_friend_request', methods=['GET', 'POST'])
def send_friend_request():
    email1 = session['email']
    print(email1)
    email2 = request.form['email']
    friendStatus = request.form['friendStatus']
    request1Status = request.form['request1Status']
    request2Status = request.form['request2Status']
    print(email1, email2, friendStatus, request1Status, request2Status)
    print(type(int(friendStatus)))
    cur = mysql.connection.cursor()
    # cur.execute('insert into friend_request values(%s, %s)', [email1, email2])
    # mysql.connection.commit()
    if int(request1Status) == 0 and int(friendStatus) == 0 and int(request2Status) == 0:
        cur.execute('insert into friend_request values(%s, %s)',
                    [email1, email2])
        mysql.connection.commit()
    elif int(request1Status) == 1:
        cur.execute('delete from friend_request where email1=%s and email2=%s', [
                    email2, email1])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email1, email2])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email2, email1])
        mysql.connection.commit()
    elif int(request2Status) == 1:
        cur.execute('delete from friend_request where email1=%s and email2=%s', [
                    email1, email2])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email1, email2])
        mysql.connection.commit()
        cur.execute('insert into friend_list values(%s, %s)', [email2, email1])
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('profile', email=email2))
    # return render_template('profile.html', ) TODO


@app.route('/news_feed')
def news_feed():
    # print("HERE")
    myEmail = session['email']
    print(myEmail)
    posts = []
    cur = mysql.connection.cursor()
    # cur.execute('select user_profile.username, post.image, post.text from user_profile inner join () on')
    cur.execute('select username, image, text, likes, email, post_id from post natural join user_profile where email in (select email2 from friend_list where email1=%s) order by timestamp', [myEmail])
    results = cur.fetchall()
    for post in results:
        temp_post = {}
        temp_post['username'] = post[0]
        temp_post['image'] = post[1].decode('utf-8')
        temp_post['text'] = post[2]
        temp_post['likes'] = post[3]
        temp_post['email'] = post[4]
        temp_post['post_id'] = post[5]
        posts.append(temp_post)
        # print("''" + str(temp_post['image'])+"''")
    return render_template('news_feed.html', myEmail=myEmail, posts=posts)

@app.route('/update_likes', methods=['POST'])
def update_likes():
    myEmail = session['email']
    poster_email = request.form['poster_email']
    post_id = request.form['post_id']
    likes = request.form['likes']
    cur = mysql.connection.cursor()
    cur.execute('select * from likes where poster_email=%s and post_id=%s and liker_email=%s', [poster_email, int(post_id), myEmail])
    results = cur.fetchall()
    print('results:', results, len(results))
    if len(results) == 0:
        cur.execute('update post set likes=%s where email=%s and post_id=%s', [int(likes)+1, poster_email, post_id])
        mysql.connection.commit()
        cur.execute('insert into likes values(%s, %s, %s)', [poster_email, post_id, myEmail])
        mysql.connection.commit()
    else:
        cur.execute('update post set likes=%s where email=%s and post_id=%s', [int(likes)-1, poster_email, post_id])
        mysql.connection.commit()
        cur.execute('delete from likes where poster_email=%s and post_id=%s and liker_email=%s', [poster_email, post_id, myEmail])
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('news_feed'))

@app.route('/upload_post', methods=['POST','GET'])
def upload_post():
    cur = mysql.connection.cursor()
    print(request.form)
    myEmail = session['email']
    cur.execute('select count(*) from post where email=%s', [myEmail])
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
        cur.execute('insert into post values(%s, %s, %s, %s, %s, %s)', [
                    myEmail, numberOfPosts[0][0] + 1, image64, text, current_timestamp, likes])
        mysql.connection.commit()
    else:
        cur.execute('insert into post values(%s, %d, %s, %s, %d, %d)', [
                    myEmail, numberOfPosts[0][0] + 1, None, text, current_timestamp, likes])
        mysql.connection.commit()
    cur.close()
    return redirect(url_for('news_feed'))


@app.route('/search_profile', methods=['GET', 'POST'])
def search_profile():
    cur = mysql.connection.cursor()
    cur.execute('select email,username from user_profile')
    results = cur.fetchall()
    cur.close()
    # print(results)
    return jsonify(results)


@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    myEmail = session['email']
    print(myEmail)
    username = request.form['username']
    cur = mysql.connection.cursor()
    cur.execute(
        'select email,username,photo from user_profile where username=%s', [username])
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
    return render_template('display_profiles.html', myEmail=myEmail, profiles=user_list)

@app.route('/chat/<email>', methods=['POST'])
def chat(email):
    myEmail = session['email']
    print(myEmail + ' - ' + email)
    cur = mysql.connection.cursor()
    cur.execute('select username from user_profile where email=%s', [email])
    res = cur.fetchall()
    username = res[0][0]

    message_sent = request.form['message_to_send']
    print('message:' + message_sent + ";")
    cur.execute('select unix_timestamp()')
    current_timestamp = cur.fetchall()
    print(current_timestamp)
    if message_sent != '':
        cur.execute('insert into chat values(%s, %s, %s, %s)', [myEmail, email, message_sent, current_timestamp[0][0]])
        mysql.connection.commit()
        cur.connection.commit()
        cur.close()
    # print(email)
    #fetching friends for sidebar
    cur.execute('select email2, username from friend_list inner join user_profile on email2=email where email1=%s', [myEmail])
    res = cur.fetchall()
    friends = []
    for item in res:
        temp_friend = {}
        temp_friend['email'] = item[0]
        temp_friend['username'] = item[1]
        friends.append(temp_friend)

    #fetching messages for chat
    messages = []
    if email == myEmail:
        pass
    else:
        cur.execute('select * from chat where (email1=%s and email2=%s) or (email1=%s and email2=%s) order by timestamp', [myEmail, email, email, myEmail])
        res = cur.fetchall()
        for item in res:
            temp_message = {}
            temp_message['email1'] = item[0]
            temp_message['email2'] = item[1]
            temp_message['text'] = item[2]
            temp_message['timestamp'] = datetime.fromtimestamp(item[3]).strftime('%Y-%m-%d %H:%M:%S')
            messages.append(temp_message)

    return render_template('chat.html',myEmail=myEmail, friends=friends, messages=messages, email=email, username=username)

# @app.route('/update_chat_message', methods=['POST'])
# def update_chat_message:
#     myEmail = session['email']
#     friends = request.form['friends']
#     # messages = messages
#     email= request.form['email']
#     username= request.form['username']
#     return render_template('chat.html', )

@socketio.on('email', namespace='/private')
def receive_username(email):
    users[email] = request.sid
    # cur = mysql.connection.cursor()
    # cur.execute('insert into socket values(%s, %s)', [email, request.sid])
    # mysql.connection.commit()
    # cur.close()
    print('email added!')


@socketio.on('private_message', namespace='/private')
def private_message(payload):
    # cur = mysql.connection.cursor()
    # cur.execute()
    recipient_session_id = users[payload['email']]
    message = payload['message']   
    print(recipient_session_id, message) 
    cur = mysql.connection.cursor()
    myEmail = session['email']
    cur.execute('select unix_timestamp()')
    current_timestamp = cur.fetchall()
    cur.execute('insert into chat values(%s,%s,%s,%s)', [myEmail, payload['email'], message, current_timestamp[0][0]])
    cur.connection.commit()
    cur.close()
    emit('new_private_message', message, room=recipient_session_id, include_self=True)

if __name__ == '__main__':

    app.secret_key = 'acquaintance'
    socketio.run(app,debug=True)

