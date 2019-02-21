import difflib

from . import hanjaro
from . import compat2unified
from . import zh2hans


def is_chinese_char(c):
    return (0x4e00  <= c <= 0x9fff  or # CJK Unified Ideographs 
            0x3400  <= c <= 0x4d8f  or # CJK Unified Ideographs Extension A 
            0x20000 <= c <= 0x2a6df or # CJK Unified Ideographs Extension B      
            0x2a700 <= c <= 0x2b73f or # CJK Unified Ideographs Extension C      
            0x2b740 <= c <= 0x2b81f or # CJK Unified Ideographs Extension D      
            0x2b820 <= c <= 0x2ceaf or # CJK Unified Ideographs Extension E      
            0xf900  <= c <= 0xfaff  or # CJK Compatibility Ideoggraphs
            0x2f800 <= c <= 0x2fa1f)   # CJK Compatibility Ideographs Supplement


class ChunkedNdiff(object):

    def __init__(self, a, b):
        self.a, self.b = a, b
        
        self.ret = []
        self.buffer = []
        self.last = None

    def flush(self):
        if self.last is not None and self.buffer:
            self.ret.append((self.last, "".join(self.buffer)))
        self.buffer = []
        self.last = None

    def diff(self):
        for d, _, c in difflib.ndiff(self.a, self.b):
            if d != self.last:
                self.flush()
            self.last = d
            self.buffer.append(c)
        self.flush()
        return self.ret


def chunked_ndiff(a, b):
    return ChunkedNdiff(a, b).diff()


class HanjaroTagger(object):

    def __init__(self, hanjaro: hanjaro.Hanjaro, 
                 unified_cjk: bool = False,
                 simplified_han: bool = False):
        self.hj = hanjaro
        self.unified_cjk = unified_cjk
        self.simplified_han = simplified_han

        self.compat2unified = None
        self.zh2hans = None

        if self.unified_cjk:
            self.compat2unified = compat2unified.Compat2Unified()
        if self.simplified_han:
            self.zh2hans = zh2hans.Zh2Hans()

    def stratify(self, ko, hj):
        ret = []
        chunks = chunked_ndiff(ko, hj)
        for (d1, chunk1), (d2, chunk2) in zip(chunks, chunks[1:]):
            assert d1 != "-" and d2 != "-", \
                f"unexpected operator from korean to hanja tag: '{d1}/{d2}'"
            if d1 == "+":
                continue
            assert d1 != d2, \
                f"two adjacent chunks cannot be both additions: '{chunk1}/{chunk2}"
            assert chunk2[0] == "(" and chunk2[-1] == ")", \
                f"additive chunk is not properly surrounded in parentheses: {chunk2}"
            cn = chunk2[1:-1]
            assert len(cn) <= len(chunk1), \
                f"length of hanja must be shorter than "\
                f"the Korean chunk: {len(cn)} > {len(chunk1)}"
            ret.append(" " * (len(chunk1) - len(cn)) + cn)
        assert chunks[-1][0] == " ", \
            f"unexpected operator from the last chunk: '{chunks[-1][0]}'"
        ret.append(" " * len(chunks[-1][1]))
        return "".join(ret)

    def tag(self, s):
        cn = self.hj.query(s)
        tags = self.stratify(s, cn)
        if self.unified_cjk:
            tags = self.compat2unified.convert(tags)
        if self.simplified_han:
            tags = self.zh2hans.convert(tags)
        return tags

