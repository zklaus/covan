from pathlib import Path
from typing import Annotated

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


if __name__ == "__main__":
    app()
