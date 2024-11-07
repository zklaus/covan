import re

from coverage import CoverageData
import pandas as pd


class Coverage:

    TEST_ID_REGEX = re.compile(r"(?P<filename>[^:]*)::(?:(?P<class>[^:]*)::)?(?P<id>[^[]*)(?:\[(?P<params>.*)\])?\|(?P<phase>.*)")

    def __init__(self, filename):
        self.data = CoverageData(filename)
        self.data.read()

    @classmethod
    def parse_test_id(cls, test_id):
        match = cls.TEST_ID_REGEX.fullmatch(test_id)
        if match is None:
            raise RuntimeError("Could not parse test id {}", test_id)
        return match.groups()

    def contexts_for_lines(self, path, lines=None):
        files = {f for f in self.data.measured_files() if f.endswith(path)}
        contexts = set().union(*[set().union(*ctxs) for ctxs in [self.data.contexts_by_lineno(file).values() for file in files]])
        contexts.remove('')
        return contexts

    def parse_contexts(self, contexts):
        df = pd.DataFrame.from_records(map(self.parse_test_id, contexts), columns=["file", "class", "id", "params", "phase"])
        tests = df.groupby(["file", "class", "id"], dropna=False).agg(lambda x: ", ".join([str(e) for e in x])).sort_index()
        return tests

    def print_contexts(self, contexts):
        ctxs = sorted(c.rsplit("|", 1)[0] for c in contexts)
        for c in ctxs:
            print(f"- [ ] {c}")
