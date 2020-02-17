"""
    Модуль для получения файлов в текущей директории.
    Используетя для задачи "Просмотр файлов"
    Автор: Валерий Козяр
    Версия: 1.0.0
"""

import os


def replace_in_web(current_path: str) -> str:
    """ Функция для замены символов | на системные разделители

    :param current_path: путь, в котором надо заменить
    :return: исправленный путь
    """
    return current_path.replace(os.path.sep, "|")


def replace_in_desk(current_path: str) -> str:
    """ Функция для замены всех системных разделителей на символ |

    :param current_path: путь, в котором надо заменить
    :return: исправленный путь
    """
    return current_path.replace("|", os.path.sep)


def get_split_path(current_path: str) -> list:
    """ Функция для получения пути ко всем папкам в указанном пути

    :param current_path: путь, который надо разложить на подпути
    :return: список, содержащий пути ко всем папкам в исходном пути от корня до текущей папки
    """

    result = []
    # пока путь не указывает на корень
    # while not os.path.ismount(current_path):
    while os.path.split(current_path)[1] != "":
        # добавляем путь в результат и записываем в путь каталог выше
        result.append(current_path)
        current_path = os.path.split(current_path)[0]
    # записываем корень
    result.append(current_path)
    result.reverse()
    return result


def list_dir(new_path: str) -> dict:
    """ Функция для получения словаря, который содержит:
    bread - список всех промежуточный путей от корня до текущей директории
            в виде словарей {"foldername": "Имя_текущей_папки",
                             "folderfullname": "Путь_до_текущей_папки"}
    filelist - список из текущих папок и файлов в данной директории
               в видк словаря {'filename': "Имя_файла",
                               'size': размер_файла_в_байтах (для папок - 0),
                               'type': "Тип",  # может быть "file", "folder", "unknown"
                               'fullfilename': "Полный_путь_до_файла/папки"}

    :param new_path: путь для разбора
    :return: словарь {"bread": [...], "filelist": [...]}
    """

    # переменные, где храняться экземпляры папок, файлов и неизвестного типа
    folder = []
    file = []
    unknown = []
    # результат определяем как словарь (будет содержать два ключа {"bread": [...], "filelist": [...]})
    result = dict()
    # разделитель между каталогами
    sep = os.path.sep
    # если путь уже заканчивается на разделитель (то есть находимся в корне),
    # то при формировании полного пути к подкаталогам и файлам не будем добавлять их
    if new_path.endswith(os.path.sep):
        sep = ""

    # обходим все объекты в папке
    for obj in os.listdir(new_path):
        current_path = new_path + sep + obj
        if os.path.isfile(current_path):
            file.append({'filename': obj,
                         'size': os.path.getsize(current_path),
                         'type': 'file',
                         'fullfilename': replace_in_web(current_path)})  # urp.quote(

        elif os.path.isdir(current_path):
            folder.append({'filename': obj,
                           'size': 0,
                           'type': 'folder',
                           'fullfilename': replace_in_web(current_path)})  # urp.quote(
        else:
            unknown.append({'filename': obj,
                            'size': 0,
                            'type': 'unknown',
                            'fullfilename': replace_in_web(current_path)})  # urp.quote(
    # сортируем по имени
    folder.sort(key=lambda rec: rec.get('filename'))
    file.sort(key=lambda rec: rec.get('filename'))
    unknown.sort(key=lambda rec: rec.get('filename'))
    # если это не корень, то добавляем в начало возврат на папку выше
    # if not os.path.ismount(new_path):
    if os.path.split(new_path)[1] != "":
        back = {'filename': "..",
                'size': 0,
                'type': 'folder',
                'fullfilename': replace_in_web(os.path.split(new_path)[0])}
        folder.insert(0, back)
    result["filelist"] = folder + file + unknown

    # получаем составляющие текущего пути ("хлебные крошки")
    bread = []
    for current_path in get_split_path(new_path):
        split_path = os.path.split(current_path)
        if split_path[1] == "":
            bread.append({"foldername": split_path[0],
                          "folderfullname": replace_in_web(split_path[0])})  # urp.quote(
        else:
            bread.append({"foldername": split_path[1],
                          "folderfullname": replace_in_web(current_path)})  # urp.quote(

    result["bread"] = bread

    return result
