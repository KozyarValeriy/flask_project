import os

from app import app
from flask import render_template
from flask import jsonify
from flask import request
from app import FileManager, Filer
from ExternalModule import Parser


FILES_WITHOUT_HEADER = ('.py', '.html', '.css', '.js')


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
    if filename.endswith(FILES_WITHOUT_HEADER):
        header = False
    else:
        header = True
    # if os.path.getsize(filename) > 10000000:
    start = int(request.args.get('startByte')) if request.args.get('startByte') else 0
    row_count = int(request.args.get('countLines')) if request.args.get('countLines') else 100
    query = request.args.get('query')
    # stop = int(request.args.get('stop')) if request.args.get('stop') else 500
    print(start, row_count, query)
    print(os.path.getsize(filename))

    file = Parser.WindowFromFile(filename, header=header)
    result = file.get_numbers_rows(start, row_count)
    # result["query"] = query
    return jsonify(result)
    # result = Filer.file_to_json(filename, header=header)
    # # result["query"] = query
    # return jsonify(result)


@app.route('/api/v1/openfile/<filename>/<int:start>/<int:row_count>')
def open_big_file(filename, start, row_count):
    filename = FileManager.replace_in_desk(filename)
    file = Parser.WindowFromFile(filename, header=True)
    return jsonify(file.get_numbers_rows(start, row_count))


@app.route('/')
def main_page():
    return render_template("index.html")


# @app.route('/', methods=["POST", "GET"])
# def main_page():
#     if request.method == "POST":
#         query = request.form.get("query")
#         print(query)
#         query123 = request.form.get("query123")
#         print(query)
#         if query123 is None:
#             print(None)
#     else:
#         query = ""
#
#     print(query)
#     return render_template("test.html")
