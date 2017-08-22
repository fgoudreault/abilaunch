class FilesReader:
    def __init__(self, path):
        self._data = self._get_data(path)

    def _get_data(self, path):
        data = {}
        lines = self._get_lines(path)
        data[".in"] = lines[0]
        data["pseudos"] = lines[5:]
        return data

    def _get_lines(self, path):
        with open(path, "r") as f:
            lines = f.readlines()
        lines = [l.strip() if line != "\n" or line == "" for l in lines]
        return lines

    def __getitem__(self, item):
        return self._data[item]
