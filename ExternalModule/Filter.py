"""
    Скрипт получения выборки по файлам.
    Автор: Захваткин Александр
    Версия от 17.02.20.
"""


import pandas as pd


def definer(data_frame, filter_string):
    temp_frame = data_frame
    filter_list = filter_string.replace("=", "==").split("&")
    column_list = []
    operations_list = []
    values_list = []
    for item in filter_list:
        if "like" in item:
            item.split("like")
            column_list.append(item.lstrip().split("like")[0].strip())
            operations_list.append("like")
            values_list.append(item.lstrip().split("like")[1].strip())
        elif ">" in item:
            column_list.append(item.lstrip().split(">")[0])
            operations_list.append(">")
            values_list.append(item.lstrip().split(">")[1])
        elif "<" in item:
            column_list.append(item.lstrip().split("<")[0])
            operations_list.append("<")
            values_list.append(item.lstrip().split("<")[1])
        elif "==" in item:
            column_list.append(item.lstrip().split("==")[0])
            operations_list.append("==")
            values_list.append(item.lstrip().split("==")[1])
    length = len(column_list)
    for i in range(0, length):
        if operations_list[i] != 'like':
            line_str = column_list[i] + " " + operations_list[i] + " " + values_list[i]
            temp_frame = temp_frame.query(line_str)
        else:
            temp_frame = temp_frame[temp_frame[column_list[i]].str.contains(values_list[i][1:-1])]
    return temp_frame


def result(query, frame):
    frames = []
    for item in query.split("|"):
        frames.append(definer(frame, item))
    return pd.concat(frames)


def filter_frame(data_frame, filter_string):
    temp_string = filter_string
    list_of_frames = []
    fl = True
    if filter_string.count("(") == filter_string.count(")"):
        if filter_string.count("(") == 0:
            result_frame = result(filter_string, data_frame)
            fl = False
        i = 0
        while ("(" in temp_string or temp_string.count("df_") >= 1) and fl:
            last_index = temp_string.rfind("(")
            first_index = temp_string.find(")", last_index)
            sub_string = temp_string[last_index:first_index + 1]
            if temp_string.count("(") == 0:
                sub_string = temp_string
            if sub_string.count("df_") == 0:
                temp_frame = result(sub_string[1:-1], data_frame)
                temp_string = temp_string.replace(sub_string, f"df_{i}")
                i += 1
                list_of_frames.append(temp_frame)
            elif sub_string.count("df_") == 1:
                if "|" in sub_string:
                    operator = "|"
                    str_in = sub_string.replace("(", "").split("|")
                else:
                    operator = "&"
                    str_in = sub_string.replace("(", "").split("&")
                for item in str_in:
                    if "df_" in item:
                        frame_index = int(item[item.find("_") + 1])
                    else:
                        temp_frame = result(item.lstrip(), data_frame)
                current_frame = list_of_frames[frame_index]
                if operator == "|":
                    temp_frame = pd.concat([temp_frame, current_frame]).drop_duplicates()
                else:
                    temp_frame = pd.merge(temp_frame, current_frame)
                list_of_frames[frame_index] = temp_frame
                temp_string = temp_string.replace(sub_string, f"df_{frame_index}")
            elif sub_string.count("df_") > 1:
                temp_sub_string = sub_string
                if (sub_string.rfind("df_") - sub_string.find("df_")) >= 7:
                    inner_str = sub_string[sub_string.find("df_") + 5:sub_string.rfind("df_") - 1]
                    inner_res = result(inner_str, data_frame)
                    sub_string = sub_string.replace(inner_str, f"df_{i}")
                    list_of_frames.append(inner_res)
                    i += 1

                while sub_string.count("df") > 1:
                    first_index = sub_string.find("df_")
                    lst_index = sub_string.rfind("df_")
                    if "&" in sub_string[first_index:lst_index]:
                        operator = "&"
                    else:
                        operator = "|"
                    operator_index = sub_string[first_index:].find(operator)
                    first_frame_index = int(sub_string[operator_index - 1])
                    second_frame_index = int(sub_string[operator_index + 4])
                    f1, f2 = list_of_frames[first_frame_index], list_of_frames[second_frame_index]
                    if operator == "|":
                        temp_frame = pd.concat([f1, f2])
                    else:
                        temp_frame = pd.merge(f1, f2)
                    # temp_frame = pd.concat([f1,f2])
                    list_of_frames[first_frame_index] = ""
                    list_of_frames[second_frame_index] = temp_frame
                    sub_string = sub_string.replace(sub_string[operator_index - 4:operator_index + 5],
                                                    f"df_{second_frame_index}")
                temp_string = temp_string.replace(temp_sub_string, sub_string)
            if len(temp_string) == 4:
                last_frame_index = int(temp_string[temp_string.find("_") + 1])
                result_frame = list_of_frames[last_frame_index]
                break
    return result_frame


if __name__ == "__main__":
    # f_string = "(step_id > 2)|timestamp = 5 &(submission_status like 'co')"
    f_string = "(step_id<10 & timestamp>1)"
    my_frame = pd.read_csv("input/submissions_data_train.csv", sep=",")
    print(filter_frame(my_frame, f_string))
