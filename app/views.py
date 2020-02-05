import os

from app import app
from flask import render_template
from flask import jsonify
from app import FileManager


@app.route('/json')
def get_json():
    posts = [
        {'author': {'login': 'user1'},
         'body': 'message 1'},
        {'author': {'login': 'user2'},
         'body': 'message 2'},
    ]
    return jsonify(posts)


@app.route('/api/v1/openfilder/<path>')
def get_navigation(path):
    print(path)
    path = path.replace('%%', '%').replace('%', '\\')
    print(path)

    if files.is_file(path):
        print("File")
    elif files.is_dir(path):
        files.path = path

    # elif files.is_dir(files.path + '\\' + path.replace("%", "\\")):
    #     files.path = files.path + '\\' + path.replace("%", "\\")
    # # elif files.path.partition(path)[-1] != '':
    # #     files.path = "\\".join(files.path.partition(path)[0:2])
    else:
        print('Error input')
    print(files.path)
    # return jsonify(files.list_dir())

    return render_template("nav.html", files=files.list_dir())


@app.route('/api/v1/openfilder/')
def get_navigation2():
    return jsonify(files.list_dir())


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


def get_path(path):
    result = []
    while os.path.split(path)[1] != "" and os.path.split(path)[1] not in result:
        result.append(os.path.split(path)[1])
        path = os.path.split(path)[0]
    result.append(path.replace("\\", "%"))
    result.reverse()
    return result


files = FileManager.ListFiles(os.getcwd())
