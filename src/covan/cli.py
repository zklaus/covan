import math
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

from .coverage import Coverage, Spec
from .settings import settings

app = typer.Typer()


@app.command()
def find_tests(
    specs: Annotated[list[str], typer.Argument()],
    output_file: Annotated[Path, typer.Option("--output-file", "-o")],
    coverage_file: Annotated[Path, typer.Option("--coverage-file", "-c")] = ".coverage",
):
    parsed_specs = [Spec.parse_spec(spec) for spec in specs]
    cov = Coverage(coverage_file)
    contexts = cov.contexts_for_specs(parsed_specs)
    df = cov.parse_contexts(contexts)
    df.to_feather(output_file)


@app.command()
def format_contexts(contexts_file: Annotated[Path, typer.Argument()]):
    INDENTATION = " " * 2
    df = pd.read_feather(contexts_file)
    indentation_level = 0
    for file, fdf in df.groupby(level=0):
        indentation_level = 0
        print(f"{INDENTATION * indentation_level}### `{file}` (total number of test functions: {len(fdf)})\n<details>\n")
        for clazz, cdf in fdf.droplevel(0).groupby(level=0, dropna=False):
            indentation_level = 0
            if isinstance(clazz, float) and math.isnan(clazz):
                pass
            else:
                print(f"{INDENTATION * indentation_level}- [ ] `{clazz}`")
                indentation_level = 1
            for function in cdf.droplevel(0).index:
                print(f"{INDENTATION * indentation_level}- [ ] `{function}`")
        print("</details>\n")


if __name__ == "__main__":
    app()
