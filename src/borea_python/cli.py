import json
from pathlib import Path
from typing import Optional

import click

from .config_parser import ConfigParser
from .generator import SDKGenerator
from .helpers import Helpers
from .models.borea_config_models import BoreaConfig
from .openapi_parser import OpenAPIParser


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx) -> None:
    """Borea Python Client Generator CLI.

    Generate Python SDK clients from OpenAPI specifications.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(name="init")
def init() -> None:
    """Initialize a new Borea configuration file (borea.config.json)."""
    config_path = Path("borea.config.json")

    # Check if config file already exists
    if config_path.exists():
        if not click.confirm(
            "borea.config.json already exists. Overwrite?", default=False
        ):
            click.echo("Initialization cancelled.")
            return

    # Create default config
    default_config = {
        "input": {"openapi": ["openapi.json"]},
        "output": {
            "clientSDK": "",
            "models": "models",
            "tests": False,
            "xCodeSamples": False,
        },
        "ignores": [],
    }

    # Write config to file
    with open(config_path, "w") as f:
        json.dump(default_config, f, indent=2)

    click.echo(f"Created borea.config.json with default settings.")


@cli.command(name="generate")
@click.option(
    "--openapi-input",
    "-i",
    help="Path to OpenAPI specification file or URL",
    type=str,
)
@click.option(
    "--sdk-output",
    "-o",
    help="Output directory for the generated SDK",
    type=str,
)
@click.option(
    "--models-output",
    "-m",
    help="Output directory for the generated models",
    type=str,
)
@click.option(
    "--tests",
    "-t",
    help="Generate tests",
    default=None,
)
@click.option(
    "--x-code-samples",
    "-x",
    help="Generate x-code-samples",
    default=None,
)
@click.option(
    "--config",
    "-c",
    help="Path to borea.config.json",
    type=str,
)
def generate(
    openapi_input: Optional[str],
    sdk_output: Optional[str],
    models_output: Optional[str],
    tests: Optional[bool],
    x_code_samples: Optional[bool],
    config: Optional[str],
):
    """Generate a Python SDK from an OpenAPI specification.

    The OpenAPI specification can be provided as a local file path or a URL.
    For URLs, both JSON and YAML formats are supported.
    """
    # Default values
    default_config = "borea.config.json"
    default_input = "openapi.json"
    # default_sdk_output is defined below
    default_models_dir = "models"
    default_tests = False
    default_x_code_samples = False

    # Load borea config
    borea_config: BoreaConfig = ConfigParser.from_source(config, default_config)

    # Use defaults if CLI args OR config values are not provided
    openapi_input = openapi_input or borea_config.input.openapi or default_input
    parser = OpenAPIParser(openapi_input)
    metadata = parser.parse()

    default_sdk_output = Helpers.clean_file_name(metadata.info.title)
    sdk_output_path = Path(
        sdk_output or borea_config.output.clientSDK or default_sdk_output
    )
    models_output_path = Path(
        sdk_output_path
        / (models_output or borea_config.output.models or default_models_dir)
    )
    tests = tests or borea_config.output.tests or default_tests
    x_code_samples = (
        x_code_samples or borea_config.output.xCodeSamples or default_x_code_samples
    )

    generator = SDKGenerator(
        metadata=metadata,
        output_dir=sdk_output_path,
        models_dir=models_output_path,
        generate_tests=tests,
        generate_x_code_samples=x_code_samples,
        borea_config=borea_config,
    )
    generator.generate()

    click.echo(f"Successfully generated SDK in: {sdk_output_path}")


if __name__ == "__main__":
    cli()
