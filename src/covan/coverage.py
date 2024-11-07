import fnmatch
from pathlib import Path
import re
from typing import Iterable, NamedTuple

from coverage import CoverageData
import pandas as pd


class Spec(NamedTuple):
    path: Path
    lines: set[int] | None

    @classmethod
    def _parse_spec(cls, spec: str | None):
        if ":" in spec:
            lines = set()
            path, line_specs = spec.split(":")
            for no_or_range in (tuple(line_spec.split("-")) for line_spec in line_specs.split(",")):
                if len(no_or_range) == 1:
                    lines.add(int(no_or_range[0]))
                else:
                    first = int(no_or_range[0])
                    last = int(no_or_range[1])
                    lines |= set(range(first, last + 1))
        else:
            path = spec
            lines = None
        return cls(path, lines)
    

class TestId(NamedTuple):
    file: Path
    clazz: str
    function: str
    params: str
    phase: str


class Coverage:
    TEST_ID_REGEX = re.compile(
        r"(?P<filename>[^:]*)::(?:(?P<class>[^:]*)::)?(?P<id>[^[]*)(?:\[(?P<params>.*)\])?\|(?P<phase>.*)"
    )
    EMPTY_CONTEXT = {""}

    def __init__(self, filename: Path):
        self.data = CoverageData(filename)
        self.data.read()

    @classmethod
    def parse_test_id(cls, test_id: str) -> TestId:
        match = cls.TEST_ID_REGEX.fullmatch(test_id)
        if match is None:
            raise RuntimeError("Could not parse test id {}", test_id)
        return TestId(*match.groups())

    def contexts_for_spec(self, spec: Spec):
        files = {f for f in self.data.measured_files() if fnmatch.fnmatch(f, spec.path)}
        if spec.lines is None:
            contexts = set()
            for file in files:
                contexts |= set().union(*[set(v) for v in self.data.contexts_by_lineno(file).values()])
        else:
            contexts = set()
            for file in files:
                for lineno, ctxs in self.data.contexts_by_lineno(file).items():
                    if lineno in spec.lines:
                        contexts |= set(ctxs)
        return contexts - self.EMPTY_CONTEXT
    
    def contexts_for_specs(self, specs: Iterable[Spec]):
        contexts = set()
        for spec in specs:
            new_contexts = self.contexts_for_spec(spec)
            contexts |= new_contexts
        return contexts

    def parse_contexts(self, contexts):
        df = pd.DataFrame.from_records(
            map(self.parse_test_id, contexts), columns=["file", "class", "id", "params", "phase"]
        )
        tests = (
            df.groupby(["file", "class", "id"], dropna=False).agg(lambda x: ", ".join([str(e) for e in x])).sort_index()
        )
        return tests

    def print_contexts(self, contexts):
        ctxs = sorted(c.rsplit("|", 1)[0] for c in contexts)
        for c in ctxs:
            print(f"- [ ] {c}")
