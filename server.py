from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)


@app.route('/news_feed')
def news_feed():
    return render_template('news_feed.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/')
def identify():
    return render_template('identify.html')


@app.route('/credentials', methods=['GET', 'POST'])
def credentials():
    if request.method == 'POST':
        # IF present go to login for password
        if request.form['email'] == 'admin@admin.com':
            return render_template('login.html', email=request.form['email'])
        else:   # otherwise go to signup
            return render_template('signup.html', email=request.form['email'])
    return


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == '__main__':
    app.run()
