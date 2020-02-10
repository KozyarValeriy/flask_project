import os


from ExternalModule import ItemInCSV


def file_to_json(filename: str, header=True) -> dict:
    """
    Функция для получения содержания файла в виде словаря

    :param filename: имя файла
    :param header: наличие заголовка в файле (по умолчанию True)
    :return: словарь в виде
            {"header": [cell_head_1, cell_head_2, ... , cell_head_N],
             "types":  [cell_type_1, cell_type_2, ... , cell_type_N],
             "data":  [[cell_1, cell_2, ... , cell_N],
                       [cell_1, cell_2, ... , cell_N]]}

    """
    # определяем текущую попытку как нулевую. Используется для поптки открытия файла в разных кодировках
    attempt = 0
    # определяем кодировку по умолчанию как UTF-8
    encoding = "UTF-8"
    result = dict()
    if os.path.exists(filename) and os.path.isfile(filename):
        while attempt < 2:
            try:
                with open(filename, encoding=encoding) as file:
                    # читаем первую строку и получаем разделитель
                    first_line = file.readline().rstrip()
                    sep = ItemInCSV.get_separator(first_line)
                    # получаем список из заголовков
                    head = []
                    for cell_head in first_line.split(sep):
                        head.append(cell_head)
                    # получаем список из списков, в которых лежат значения в каждой ячейке по строке
                    data = []
                    for row in file.readlines():
                        line = []
                        for cell_data in row.rstrip().split(sep):
                            line.append(cell_data)
                        data.append(line)
                    result["stopByte"] = file.tell()
                # если файл с заголовком, то добавляем его в результат
                if header:
                    result['header'] = head
                # если файл не содержит заголовка, добавляем первую строку в начало списка со строками
                # а в качестве заголовка используем None
                else:
                    data.insert(0, head)
                    result['header'] = ['null'] * len(head)

                result['data'] = data
                # получаем типы для столбцов в файле и добавляем результат в ответ
                types = ItemInCSV.get_types(filename, encoding=encoding, separator=sep, header=header)

                result['types'] = types
                break
            except UnicodeDecodeError as e:
                # если была ошибка в кодировке, увеличиваем счетчик ошибок
                # и пробуем открыть с кодировкой по умолчанию
                attempt += 1
                encoding = None
            except Exception as e:
                print(f"Error: \n{e}")
                break

    return result
