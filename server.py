from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def news_feed():
    return render_template('news_feed.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run()