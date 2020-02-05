import os


class ListFiles:
    def __init__(self, start_path: str):
        self._path = start_path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path: str):
        if os.path.isdir(new_path):
            self._path = new_path
        elif os.path.isdir(self._path + "\\" + new_path):
            self._path = self._path + "\\" + new_path
        else:
            print("It's not a dir")

    def list_dir(self):
        dir = []
        file = []
        unknown = []
        result = {}
        for obj in os.listdir(self._path):
            if os.path.isfile(self._path + "\\" + obj):
                file.append({'filename': obj,
                             'size': os.path.getsize(self._path + "\\" + obj),
                             'type': 'file',
                             'fullfilename': self._path + "\\" + obj})

            elif os.path.isdir(self._path + "\\" + obj):
                dir.append({'filename': obj,
                            'size': 0,
                            'type': 'folder',
                            'fullfilename': self._path + "\\" + obj})
            else:
                unknown.append({'filename': obj,
                                'size': 0,
                                'type': 'unknown',
                                'fullfilename': self._path + "\\" + obj})

        dir.sort(key=lambda rec: rec.get('filename'))
        file.sort(key=lambda rec: rec.get('filename'))
        unknown.sort(key=lambda rec: rec.get('filename'))

        if not os.path.ismount(self._path):
            dir = [{'filename': "..",
                    'size': 0,
                    'type': 'folder',
                    'fullfilename': os.path.split(self._path)[0]}] + dir

        result["filelist"] = dir + file + unknown

        bread = []
        for current_path in self.split_path():
            if os.path.split(current_path)[1] == "":
                bread.append({"foldername": os.path.split(current_path)[0],
                              "folderdullname": os.path.split(current_path)[0]})
            else:
                bread.append({"foldername": os.path.split(current_path)[1],
                              "folderdullname": current_path})
        result["bread"] = bread

        return result

    def back(self):
        self._path = os.path.split(self._path)[0]

    def is_file(self, path: str) -> bool:
        if os.path.isfile(path) or os.path.isfile(self._path + "\\" + path):
            return True
        return False

    def is_dir(self, path: str) -> bool:
        if os.path.isdir(path) or os.path.isdir(self._path + "\\" + path):
            return True
        return False

    def split_path(self):
        result = []
        path = self.path
        while os.path.split(path)[1] != "" and path not in result:
            result.append(path)
            path = os.path.split(path)[0]
        result.append(path)
        result.reverse()
        return result

