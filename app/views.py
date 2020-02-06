import os

from app import app
from flask import render_template
from flask import jsonify
from app import FileManager


@app.route('/api/v1/openfolder/<path>')
def folder_navigation(path):
    desk_path = FileManager.replace_in_desk(path)
    if os.path.isdir(desk_path):
        return jsonify(FileManager.list_dir(desk_path))
    else:
        return jsonify(FileManager.list_dir(os.getcwd()))


@app.route('/api/v1/openfolder/')
def get_navigation2():
    desk_path = FileManager.replace_in_desk(os.getcwd())
    return jsonify(FileManager.list_dir(desk_path))


@app.route('/api/v1/openfile/<filename>')
def open_file(filename):
    filename = FileManager.replace_in_desk(filename)
    with open(filename, encoding='utf-8') as file:
        result = file.readlines()
    return str(result)
    # return f"Open file: {filename}\n{result}"


@app.route('/')
def main_page():
    return render_template("index.html")
