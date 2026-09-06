from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table

from .db import DEFAULT_DB, init_db, top_articles
from .pipeline import DEFAULT_SOURCES, run_ingestion


app = typer.Typer(help="Nippon Signal — Japan technology signal intelligence.")
console = Console()


@app.command("init-db")
def init_database(db: Path = typer.Option(DEFAULT_DB, help="SQLite database path")):
    init_db(db)
    console.print(f"[green]Initialized[/green] {db}")


@app.command()
def ingest(
    sources: Path = typer.Option(DEFAULT_SOURCES, help="YAML source config"),
    db: Path = typer.Option(DEFAULT_DB, help="SQLite database path"),
):
    result = run_ingestion(sources, db)
    console.print(
        f"[green]Fetched {result['fetched']}[/green] | "
        f"inserted {result['inserted']} | duplicates {result['duplicates']}"
    )
    for source, error in result["errors"]:
        console.print(f"[yellow]Feed error[/yellow] {source}: {error}")


@app.command("top")
def show_top(
    limit: int = typer.Option(20, min=1, max=100),
    db: Path = typer.Option(DEFAULT_DB, help="SQLite database path"),
):
    rows = top_articles(limit=limit, db_path=db)
    table = Table(title=f"Top {limit} Nippon Signals")
    table.add_column("Score", justify="right")
    table.add_column("Category")
    table.add_column("Source")
    table.add_column("Title")

    for row in rows:
        table.add_row(
            f"{row['signal_score']:.1f}",
            row["category"],
            row["source"],
            row["title"],
        )
    console.print(table)


if __name__ == "__main__":
    app()
