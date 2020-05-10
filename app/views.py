"""
    Роутер.
    Автор: Валерий Козяр
    Версия 1.0.0
"""


import os

from app import app
from flask import render_template
from flask import jsonify
from flask import request

from app import FileManager
from ExternalModule import Parser, QueryTask, Filter


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
    file = Parser.WindowFromFile(filename, header=header)
    # получение GET параметров
    start = QueryTask.string_to_int(request.args.get('startByte'), default=0)
    row_count = QueryTask.string_to_int(request.args.get('countLines'), default=100)
    query = request.args.get('query')
    step = request.args.get('step')
    if step == "prev":
        result = file.get_previous_numbers_rows(start, row_count)
    else:
        result = file.get_numbers_rows(start, row_count)
    # обработка фильтрации, если есть в запросе
    if query is not None:
        df = QueryTask.get_DataFrame_from_JSON(result)
        # получение DataFrame с наложенными фильтрами
        df = Filter.filter_frame(df, query)
        result = QueryTask.get_JSON_from_DataFrame(df, result["startByte"], result["stopByte"], result["types"])
        # добавление строк, если в результате получили меньше row_count
        start = result["startByte"]
        new_row_count = row_count
        while len(result["data"]) < row_count and result["stopByte"] < file.size:
            if len(result["data"]) > row_count / 2:
                new_row_count *= 4
            else:
                new_row_count *= 10
            result = file.get_numbers_rows(start, new_row_count)
            df = QueryTask.get_DataFrame_from_JSON(result)
            # получение DataFrame с наложенными фильтрами
            df = Filter.filter_frame(df, query)
            result = QueryTask.get_JSON_from_DataFrame(df, result["startByte"], result["stopByte"], result["types"])
        result["data"] = result["data"][:row_count]
    return jsonify(result)


@app.route('/api/v1/openfile/<filename>/<int:start>/<int:row_count>')
def open_big_file(filename, start, row_count):
    filename = FileManager.replace_in_desk(filename)
    file = Parser.WindowFromFile(filename, header=True)
    return jsonify(file.get_numbers_rows(start, row_count))


@app.route('/')
def main_page():
    return render_template("index.html")
