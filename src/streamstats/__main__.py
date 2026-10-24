import typer

from streamstats.analysis import analyze
from streamstats.errors import StreamStatsError
from streamstats.models import SkipStats
from streamstats.parsers import files_reader
from streamstats.report import report

app = typer.Typer()


@app.callback()
def cli():
    """Read CSV or JSONL files and create a JSON report."""


@app.command("analyze")
def main(
    inputs: list[str],
    file_format: str = typer.Option(..., "--format"),
    output: str = typer.Option("report.json", "--output"),
    skip_invalid: bool = typer.Option(False, "--skip-invalid"),
) -> None:
    try:
        skip_stats = SkipStats()
        events = files_reader(
            inputs, file_format, skip_stats, skip_invalid=skip_invalid
        )
        analysis_stats = analyze(events)
        report(analysis_stats, skip_stats, output)
    except (ValueError, StreamStatsError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
