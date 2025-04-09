import click


class Logger:
    @classmethod
    def log(cls, message: str):
        click.echo(message)

    @classmethod
    def warn(cls, message: str):
        click.echo(f"WARNING: {message}")

    @classmethod
    def error(cls, message: str):
        click.echo(f"ERROR: {message}")
