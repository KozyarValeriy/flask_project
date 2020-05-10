"""
    Преобразование DataFrame в JSON и обратно.
    Автор: Валерий Козяр
    Версия 1.0.1
"""


import pandas as pd


def get_DataFrame_from_JSON(start_dict: dict) -> pd.DataFrame:
    """ Функция для получения DataFrame из JSON """
    tmp_dict = dict()
    for i in range(len(start_dict['header'])):
        tmp_dict[start_dict['header'][i]] = list(cell[i] for cell in start_dict['data'])

        if start_dict['types'][i] == "int":
            try:
                tmp_dict[start_dict['header'][i]] = list(map(int, tmp_dict[start_dict['header'][i]]))
            except ValueError:
                pass

    return pd.DataFrame.from_dict(tmp_dict)


def get_JSON_from_DataFrame(df: pd.DataFrame, start_byte: int, stop_byte: int, types: list) -> dict:
    """ Функция для получения JSON из DataFrame """
    result = dict()
    result["data"] = list(list(line) for line in df.values)
    result["header"] = list(df.keys())
    result["startByte"] = start_byte
    result["stopByte"] = stop_byte
    result["types"] = types
    return result


def string_to_int(start_string: str, default) -> int:
    """ Функция для получения числа из строки

    :param start_string: строка, которую надо преобразовать в число,
    :param default: значени по умолчанию, если преобразовать не получилось,
    :return: полученное число.
    """
    try:
        number = int(start_string)
    except ValueError:
        number = default
    return number


if __name__ == "__main__":
    data = {"data": [[31971, "1434349275", "correct", 15853], [31972, "1434348300", "correct", 15853],
                     [31972, "1478852149", "wrong", 15853], [31972, "1478852164", "correct", 15853],
                     [31976, "1434348123", "wrong", 15853], [31976, "1434348188", "correct", 15853],
                     [31976, "1478852055", "correct", 15853], [31977, "1434347371", "correct", 15853],
                     [31978, "1434349981", "correct", 15853], [31979, "1434446091", "correct", 15853],
                     [31981, "1434446377", "correct", 15853], [31983, "1434445185", "correct", 15853],
                     [31986, "1434450277", "correct", 15853], [31988, "1434449974", "correct", 15853],
                     [31991, "1434521391", "correct", 15853], [32031, "1434363465", "wrong", 15853],
                     [32031, "1434363485", "correct", 15853], [32075, "1434437238", "correct", 15853],
                     [32089, "1434450470", "correct", 15853]],
            "header": ["step_id", "timestamp", "submission_status", "user_id"],
            "types": ["int", "uid", "category", "int"],
            "startByte": 0,
            "stopByte": 647}
    df_test = get_DataFrame_from_JSON(data)
    # print(df_test)
    data_2 = get_JSON_from_DataFrame(df_test, start_byte=data["startByte"],
                                     stop_byte=data["stopByte"], types=data["types"])
    # print(data_2)
    print(data_2 == data)
