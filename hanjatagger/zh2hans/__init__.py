from . import langconv


class Zh2Hans(object):

    def __init__(self):
        self.converter = langconv.Converter("zh-hans")

    def convert(self, s):
        return self.converter.convert(s)

