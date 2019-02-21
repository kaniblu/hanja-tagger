import os


class Compat2Unified(object):

    def __init__(self, map_path=None):
        self.map_path = map_path

        if self.map_path is None:
            self.map_path = os.path.join(os.path.dirname(__file__), "compat2unified.txt")
        with open(self.map_path, "r") as f:
            self.data = dict(l.rstrip().split("\t") for l in f)

    def convert(self, s):
        return "".join(self.data[w] if w in self.data else w 
                       for w in s)

