from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)


@app.route('/')
def news_feed():
    return render_template('news_feed.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/identify', methods=['GET', 'POST'])
def identify():

    return render_template('identify.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        if request.form['username'] == 'admin':  # IF present go to login for password
            return render_template('login.html', username=request.form['username'])
        else:   # otherwise go to signup
            return render_template('signup.html', username=request.form['username'])
    return


if __name__ == '__main__':
    app.run()
