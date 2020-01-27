from app import app
from flask import render_template


@app.route('/index')
def index():
    user = {"login": "in index"}
    posts = [
        {'author': {'login': 'user1'},
         'body': 'message 1'},
        {'author': {'login': 'user2'},
         'body': 'message 2'},
    ]
    return render_template("index.html", title="home", user=user, posts=posts)


@app.route('/')
def main_page():
    user = {"login": "Kozyar"}
    return render_template("index.html", user=user)
