import pandas as pd
import numpy as np


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
            str = column_list[i] + " " + operations_list[i] + " " + values_list[i]
            temp_frame = temp_frame.query(str)
        else:
            str = column_list[i] + " " + operations_list[i] + " " + values_list[i]
            temp_frame = temp_frame[temp_frame[column_list[i]].str.contains(values_list[i][1:-1])]
    return temp_frame


def result(frame, query):
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
            result_frame = result(data_frame, filter_string)
            fl = False
        i = 0
        while ("(" in temp_string or temp_string.count("df_") > 1) and fl:
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
                curent_frame = list_of_frames[frame_index]
                temp_frame = pd.concat([temp_frame, curent_frame])
                list_of_frames[frame_index] = temp_frame
                temp_string = temp_string.replace(sub_string, f"df_{frame_index}")
            elif sub_string.count("df_") > 1:
                temp_sub_string = sub_string
                while sub_string.count("df") > 1:
                    first_index = sub_string.find("df_")
                    if "&" in sub_string[first_index:]:
                        operator = "&"
                    else:
                        operator = "|"
                    operator_index = sub_string[first_index:].find(operator)
                    first_frame_index = int(sub_string[operator_index - 1])
                    second_frame_index = int(sub_string[operator_index + 4])
                    f1, f2 = list_of_frames[first_frame_index], list_of_frames[second_frame_index]
                    temp_frame = pd.concat([f1, f2])
                    list_of_frames[first_frame_index] = ""
                    list_of_frames[second_frame_index] = temp_frame
                    sub_string = sub_string.replace(sub_string[operator_index - 4:operator_index + 5],
                                                    f"df_{second_frame_index}")
                temp_string = temp_string.replace(temp_sub_string, sub_string)
            if len(temp_string) == 4:
                result_frame = list_of_frames[second_frame_index]
    return result_frame


if __name__ == "__main__":
    f_string = "step_id > 2 & step_id < 5 "
    # f_string = "(step_id < 5 | (step_id = 10 | step_id = 11))&(timestamp=3 | timestamp=4)&(timestamp = 2 |
    # submission_status like 'correct lol')"
    my_frame = pd.read_csv("input/submissions_data_train.csv", sep=",")
    print(filter_frame(my_frame, f_string))
