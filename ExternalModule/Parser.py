"""
    Скрипт для парсинга файлов любого типа.
    Задается имя файла, начальный байт и конечный байт.
    Версия: 1.0.0
"""

import os


from ExternalModule import ItemInCSV


class StartEndPositionError(Exception):
    """ Исключение при неправильных начальных и конечных позиций """
    pass


class FileError(Exception):
    """ Исключение при недоступном для чтения или позиционирования файле """
    pass


class WindowFromFile:
    """ Класс для получения целых строк в диапазоне от начального до конечного байта.

    """

    def __init__(self, filename: str, header=True, string_end=None):
        self._filename = filename
        self.header = header
        if string_end is None:
            string_end = [b"\n", b"\r", b"\r\n"]
        self._string_end = string_end
        self._line_end_char = None  # символ конца строки
        self._delimiter = None  # символ разделитель
        self._data = None  # результат предыдущей выборки

    @property
    def string_end(self):
        return self._string_end

    @property
    def filename(self):
        return self._filename

    @property
    def line_end_char(self):
        return self._line_end_char

    @property
    def delimiter(self):
        return self._delimiter

    @property
    def data(self):
        return self._data

    @staticmethod
    def increment(number: int, step: int = 1) -> int:
        """ Функция для увеличения входного числа на шаг (шаг default=1) """
        return number + step

    @staticmethod
    def decrement(number: int, step: int = 1) -> int:
        """ Функция для уменьшения входного числа на шаг (шаг default=1) """
        return number - step

    def _get_end_char(self, input_file, file_size: int):
        """ Функция для поиска символа конца строки.

        :param input_file: файл, в котором ведется поиск
        :param file_size: размер файла в байтах
        """
        # если еще не определили символ
        if self._line_end_char is None:
            step = 0
            # перебираем строки с начала, пока не встретим конец строки или пока пока не дойдем до конца файла
            while step < file_size:
                input_file.seek(step)
                char = input_file.read(2)
                # если символы равны \r\n или \r_ или \n_ (_ - любой символ)
                # так как при ситуации _\r может быть, что дальше будет \n
                if char in self._string_end or char[:1] in self._string_end:
                    char = str.encode("".join(map(chr, filter(lambda x: x <= max(ord('\n'), ord('\r')), char))))
                    self._line_end_char = char
                    break
                step += 1
            # если цикл закончился без break
            else:
                self._line_end_char = ""

    def _positioning(self, start_pos: int, limit: int, input_file, func) -> int:
        """
        Функция для поиска допустимого положения каретки.

        :param start_pos: начальная позиция картеки
        :param limit: передльное значение для картеки в файле
        :param input_file: файл, в котором ведется поиск
        :param func: функция для изменения положения каретки
        :return: допустимое значение для картеки
        """

        input_file.seek(start_pos)
        start_ch = input_file.read(len(self._line_end_char))
        # пока символ не конец строки и положение картеки еще не предельное
        while start_ch != self._line_end_char and start_pos != limit:
            start_pos = func(start_pos)
            input_file.seek(start_pos)
            start_ch = input_file.read(len(self._line_end_char))
        # при возвращении (если это не предельное положение) добавляем длину
        # сивола конца строки, чтобы при поиске в правую сторону оставить
        # его в результате а при поиске в левую сторону - исключить
        if start_pos != limit:
            return start_pos + len(self._line_end_char)
        return start_pos

    def get_row_in_window(self, start: int, end: int) -> dict:
        """
        Функция для поиска целых строк по начальному и конечному байту

        :param start: начальное положение каретки
        :param end: конечное положение каретки
        :return:  словарь в виде
                    {"header": [cell_head_1, cell_head_2, ... , cell_head_N],
                     "types":  [cell_type_1, cell_type_2, ... , cell_type_N],
                     "data":  [[cell_1, cell_2, ... , cell_N],
                               [cell_1, cell_2, ... , cell_N],
                                        ...
                               [cell_1, cell_2, ... , cell_N]],
                     "stopByte": байт_начала_окна,
                     "startByte": байт_конца_окна}
        """

        result = {}

        if start > end:
            raise StartEndPositionError("START position must be less then END position")
        with open(self._filename, "rb") as file:
            if not file.readable():
                raise FileError("File can't be read")
            if not file.seekable():
                raise FileError("File can't be seek")
            # получаем длину всего файла в байтах
            file_size = os.path.getsize(self._filename)
            # поиск символа конца строки для исходного файла
            self._get_end_char(file, file_size=file_size)
            if start > file_size:
                raise StartEndPositionError("START position must be less then size of file")
            # поиск допустимого начального значения
            start_pos = self._positioning(start_pos=start, limit=0, input_file=file, func=self.decrement)
            # если начальное смещение не ноль и требуется заголовок
            if start_pos != 0 and self.header:
                start_pos_head = 0
                end_pos_head = self._positioning(start_pos=0, limit=file_size, input_file=file, func=self.increment)
                file.seek(start_pos_head)
                header = bytes.decode(file.read(end_pos_head - start_pos_head))
                self._delimiter = ItemInCSV.get_separator(header)
                # header = header.split(self._delimiter)
            # поиск допустимого конечного значения
            if end >= file_size:
                end_pos = file_size
            else:
                end_pos = self._positioning(start_pos=end, limit=file_size, input_file=file, func=self.increment)

            # формирование результата
            file.seek(start_pos)
            # читаем полученное кол-во байт
            body = file.read(end_pos - start_pos)
            body = list(map(bytes.decode, body.rstrip().split(self.line_end_char)))
            if self._delimiter is None:
                self._delimiter = ItemInCSV.get_separator(body[0])

            if start_pos == 0 and self.header:
                header = body[0]
                body = body[1:]

            data = []
            for line in body:
                data.append(line.split(self._delimiter))

            if not self.header:
                header = self._delimiter.join(['null'] * len(data[0]))

            result["header"] = header.rstrip().split(self._delimiter)
            result['data'] = data
            result['stopByte'] = end_pos
            result['startByte'] = start_pos

        # определяем текущую попытку как нулевую. Используется для поптки открытия файла в разных кодировках
        attempt = 0
        # определяем кодировку по умолчанию как UTF-8
        encoding = "UTF-8"
        while attempt < 2:
            try:
                types = ItemInCSV.get_types(self._filename, encoding=encoding,
                                            separator=self._delimiter, header=self.header)

                result["types"] = types
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

    def get_numbers_rows(self, start: int, count: int) -> dict:
        """
        Функция для поиска указанного кол-ва строк

        :param start: начальное положение каретки
        :param count: требуемое кол-во строк
        :return: словарь в виде
                    {"header": [cell_head_1, cell_head_2, ... , cell_head_N],
                     "types":  [cell_type_1, cell_type_2, ... , cell_type_N],
                     "data":  [[cell_1, cell_2, ... , cell_N],
                               [cell_1, cell_2, ... , cell_N],
                                        ...
                               [cell_1, cell_2, ... , cell_N]],
                     "stopByte": байт_начала_окна,
                     "startByte": байт_конца_окна}
        """
        # результат для возврата
        result = {}

        with open(self._filename, "rb") as file:
            if not file.readable():
                raise FileError("File can't be read")
            if not file.seekable():
                raise FileError("File can't be seek")
            # получаем размер файла
            file_size = os.path.getsize(self._filename)
            # начальная позиция должна быть меньше размера всего файла
            if start > file_size:
                raise StartEndPositionError("START position must be less then size of file")
            # поиск символа конца строки для исходного файла
            self._get_end_char(file, file_size=file_size)
            # поиск допустимого начального значения
            start_pos = self._positioning(start_pos=start, limit=0, input_file=file, func=self.decrement)
            # если начальное смещение не ноль и требуется заголовок
            # ищем строку заголовка - начальное значение - 0, а конечное - ищем
            if start_pos != 0 and self.header:
                start_pos_head = 0
                end_pos_head = self._positioning(start_pos=0, limit=file_size, input_file=file, func=self.increment)
                # удаляем символы новой строки в конце
                end_pos_head -= len(self._line_end_char)
                file.seek(start_pos_head)
                header = bytes.decode(file.read(end_pos_head - start_pos_head))

        # определяем текущую попытку как нулевую. Используется для поптки открытия файла в разных кодировках
        attempt = 0
        # определяем кодировку по умолчанию как UTF-8
        encoding = "UTF-8"
        while attempt < 2:
            try:
                # так как теперь значем корректный байт начала, проще считывать по одной строке целиком
                with open(self._filename, "r", encoding=encoding) as file:
                    file.seek(start_pos)
                    # если стартовая позиция равна ноль и есть заголовок, то читаем строку и пропускаем ее,
                    # так как заголовок уже есть в result
                    if start_pos == 0 and self.header:
                        header = file.readline()
                    # поиск заданного кол-ва строк
                    current_count = 0
                    # читам по одной строке
                    # пока не набрали требуемое кол-во строк и пока не достигли конца файла, читаем
                    data = []
                    while current_count < count and file.tell() < file_size:
                        line = file.readline().rstrip()
                        if self._delimiter is None:
                            self._delimiter = ItemInCSV.get_separator(line)
                        data.append(line.split(self._delimiter))
                        current_count += 1

                    if not self.header:
                        header = ['null'] * len(data[0])
                    else:
                        header = header.rstrip().split(self._delimiter)

                    result["header"] = header
                    result["data"] = data
                    result['startByte'] = start_pos
                    result["stopByte"] = file.tell()
                    # определение типов столбцов
                    types = ItemInCSV.get_types(self._filename, encoding=encoding,
                                                separator=self._delimiter, header=self.header)

                    result["types"] = types
                    # print(file.tell())
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


if __name__ == "__main__":
    data_test = WindowFromFile(r'C:\work\parsing_file\input_file\output.txt', header=True)
    print(data_test.get_numbers_rows(100, 2))
    print("low")
    data_test = WindowFromFile(r'C:\work\parsing_file\input_file\test_mid.csv', header=True)
    print(data_test.get_numbers_rows(100, 2))

    data_test = WindowFromFile(r'C:\work\parsing_file\input_file\output.txt', header=True)
    print(data_test.get_row_in_window(100, 600))
    print("low")
    data_test = WindowFromFile(r'C:\work\parsing_file\input_file\test_mid.csv', header=True)
    print(data_test.get_row_in_window(100, 600))
