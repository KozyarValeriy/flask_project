"""
    Скрипт для получения разделителя, шапки и типов столбцов.
    Автор: Захваткин Александр
"""


import re

sep_list = [",", "|", ";", "\t"]


def get_separator(head):
    """
    :return: return separator from input csv file
    """
    dic = {}
    for item in sep_list:
        dic[item] = 0
    for item in sep_list:
        dic[item] = len(head.split(item))
    separator = max(dic, key=dic.get)
    return separator


def get_headers(head, separator=None):
    """
    :return: return list of heads from input csv file
    """
    if separator is None:
        separator = get_separator(head)
    header = head.split(separator)
    return header


def get_types(input_name, encoding=None, separator=None, header=True, count_line=1000):
    """
    :param: input_name: input csv path
    :return: return list of heads types in head order
    """
    heads_types = []
    # open file to read, if lines in file < 1000 , read all file, else read 1000 lines
    # regex = r"\S+@\S+"
    regex = r"(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"" \
            r"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")" \
            r"@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]" \
            r"|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:" \
            r"[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    with open(input_name, encoding=encoding) as file:
        if header:
            file.readline()
        list_items = []
        for i in range(count_line):
            list_items.append(file.readline())

        if separator is None:
            separator = get_separator(list_items[0].rstrip())
    # count items in first line
    count_items = list_items[0].count(separator) + 1
    # lines counter
    lines_counter = 0
    # loop for elements in head line
    for head in range(0, count_items):
        head_type = None
        head_dict = {'int': 0, 'string': 0, "date": 0}
        head_values = [item.strip().split(separator)[lines_counter] for item in list_items]
        # loop for elements in line to define type of column
        for value in head_values:
            # try to recognise if value is number(float,integer)
            if value.replace(".", "", 1).isdigit():
                value = 1
            # if value is in date type inrease date counter
            if (re.match(r"[0-9]{1,2}[-/.][0-9]{1,2}[-/.][0-9]{4}", str(value)) or
                    re.match(r"[0-9]{4}[-/.][0-9]{1,2}[-/.][0-9]{1,2}", str(value))) and (len(str(value)) in range(8, 11)):
                head_dict["date"] += 1
            # try to recognise if value is email
            elif re.match(regex, str(value)):
                head_type = "email"
            # try to recognise if value is unic id
            elif len(set(head_values)) == len(list_items):
                head_type = f'uid'
            # if value is int type inrease int counter
            elif type(value) == type(1) or type(value) == type(1.0):
                head_dict['int'] += 1
            # count unic elemets in rows if unic items less 50 % then type of column is category
            elif len(set(head_values)) < len(list_items) * 0.5:
                head_type = "category"
            # if value no match previous statements it's string and  increase string  counter
            else:
                head_dict["string"] += 1
        # if type of column is int,category or string define it here
        if head_type is None:
            head_type = max(head_dict, key=head_dict.get)
        # append type of column in list
        heads_types.append(head_type)
        lines_counter += 1
    return heads_types


def into_dict(input_name, head=None):
    """
    :param head:
    :param input_name: input csv path
    :return: dictionary output with data:list of all lines in csv
                                    header:list of headers
                                    types:list of headers types
    """
    output = {"data": []}
    with open(input_name) as file:
        if head is None:
            head = file.readline().strip()
        separator = get_separator(head)
        head_topics = get_headers(head, separator)
        topic_types = get_types(input_name)
        for line in file.readlines():
            output["data"].append(line.strip().split(separator))
        output["header"] = head_topics
        output["types"] = topic_types
    return output


if __name__ == "__main__":
    print(into_dict("input/train.txt", "date,male"))
