from pathlib import Path
from typing import Annotated

import typer

from .coverage import Coverage, Spec
from .settings import settings

app = typer.Typer()


@app.command()
def find_tests(
    specs: Annotated[list[str], typer.Argument()],
    coverage_file: Annotated[Path, typer.Option("--coverage-file", "-c")] = ".coverage",
):
    parsed_specs = [Spec._parse_spec(spec) for spec in specs]
    print(parsed_specs)
    cov = Coverage(coverage_file)
    contexts = cov.contexts_for_specs(parsed_specs)
    df = cov.parse_contexts(contexts)
    print(df)
    # cov.print_contexts(contexts)


if __name__ == "__main__":
    app()
