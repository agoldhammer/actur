"""Console script for actur."""
import sys
import click


@click.command()
@click.option("--pubname", "-p", multiple=True, default=["all"])
@click.option("--start", "-s")
@click.option("--end", "-e")
@click.option("--summ/--no-summ", default=True)
def main(pubname: str, start: str, end: str, summ: bool):
    """Console script for actur."""
    click.echo(pubname)
    click.echo([start, end])
    click.echo(summ)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
