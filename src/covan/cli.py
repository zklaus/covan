import typer

from .coverage import Coverage
from .settings import settings

app = typer.Typer()


@app.command()
def find_tests(coverage_file: str):
    cov = Coverage(coverage_file)
    contexts = cov.contexts_for_lines("solve.py")
    df = cov.parse_contexts(contexts)
    print(df)
    cov.print_contexts(contexts)

if __name__ == "__main__":
    app()
