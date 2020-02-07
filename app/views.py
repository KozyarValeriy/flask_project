import os

from app import app
from flask import render_template
from flask import jsonify
from flask import redirect
from flask import request
from app import FileManager, Filer
from ExternalModule import Parser


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
    print(os.path.getsize(filename))
    if os.path.getsize(filename) > 10000000:
        start = int(request.args.get('start')) if request.args.get('start') else 0
        row_count = int(request.args.get('rowCount')) if request.args.get('rowCount') else 500
        print(start, row_count)
        # return redirect(f'/api/v1/openfile/{FileManager.replace_in_web(filename)}/0/500')
        file = Parser.WindowFromFile(filename, header=True)
        return jsonify(file.get_numbers_rows(start, row_count))
    return jsonify(Filer.file_to_json(filename, header=True))


@app.route('/api/v1/openfile/<filename>/<int:start>/<int:row_count>')
def open_big_file(filename, start, row_count):
    filename = FileManager.replace_in_desk(filename)
    file = Parser.WindowFromFile(filename, header=True)
    return jsonify(file.get_numbers_rows(start, row_count))


@app.route('/')
def main_page():
    return render_template("index.html")
