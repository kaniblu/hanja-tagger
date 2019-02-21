import urllib.parse as urlparse

import requests
from bs4 import BeautifulSoup


def merge_dict(a, b):
    a = {k: v for k, v in a.items()}
    a.update(b)
    return a


class Hanjaro(object):

    HOST = "hanjaro.juntong.or.kr"
    PATH = "/text_translater.aspx"
    INPUT_FIELDS = {
        "__VIEWSTATE", 
        "__VIEWSTATEGENERATOR", 
        "__EVENTVALIDATION", 
        "TextBox3"
    }
    TEXTAREA_FIELDS = {f"TextBox{i}" for i in range(1, 3)}
    OPTIONS = merge_dict({
        "ddlLanguage": "1",
        "1": "RadioButton2",
        "ImageButton1.x": "120",
        "ImageButton1.y": "20"
    }, {f"CheckBox{i}": "on" for i in range(1, 9)})

    def __init__(self):
        self.session = None
        self.data = None
        self.url = self.get_url(self.PATH)

    def open(self):
        self.session = requests.Session()

    def close(self):
        if self.session is not None:
            self.session.close()

    def __enter__(self):
        self.open()
        return self

    def get_url(self, path):
        return urlparse.urljoin(f"http://{self.HOST}", path)

    def request(self, data=None, post=False):
        assert self.session is not None, \
            "make sure to call `self.open()` beforehand"
        method_kwargs = dict()
        if post:
            method = self.session.post
            if self.data is not None:
                if data is not None:
                    method_kwargs = {"data": merge_dict(self.data, data)}
                else:
                    method_kwargs = {"data": self.data}
        else:
            method = self.session.get
        resp = method(self.url, **method_kwargs)
        assert resp.status_code / 100 == 2, \
            f"something went wrong with the request. status code: {resp.status_code}"
        bs = BeautifulSoup(resp.content.decode(), features="html.parser")
        self.url = self.get_url(bs.find(id="form1").attrs["action"])
        self.data = dict()
        self.data.update({f: bs.find(id=f).attrs["value"] 
                          for f in self.INPUT_FIELDS})
        self.data.update({f: bs.find(id=f).text
                          for f in self.TEXTAREA_FIELDS})
        self.data.update(self.OPTIONS)
        tb2 = bs.find(id="TextBox2")
        if tb2 and tb2.text:
            return tb2.text.strip()
        else:
            return

    def query(self, q):
        if self.data is None:
            self.request(post=False)
        return self.request(data=dict(TextBox1=q), post=True)

    def __exit__(self, *exc):
        self.close()

