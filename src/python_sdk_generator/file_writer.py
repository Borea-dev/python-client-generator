import json
from pathlib import Path
from typing import List, Optional
import fnmatch

import click


class ConfigurableFileWriter:
    """A file writer that respects ignore patterns specified in a config file."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the file writer with an optional config path.
        If no config path is provided, it will look for borea.config.json in the current directory.
        """
        self.config_path = (
            Path(config_path) if config_path else Path("borea.config.json")
        )
        self.ignore_patterns: List[str] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load the configuration file and extract ignore patterns."""
        try:
            with open(self.config_path) as f:
                config = json.load(f)
                self.ignore_patterns = config.get("ignores", [])
        except FileNotFoundError:
            click.echo(
                f"Warning: Config file {self.config_path} not found. No ignore patterns will be applied."
            )
            self.ignore_patterns = []
        except json.JSONDecodeError:
            click.echo(f"Error: Config file {self.config_path} is not valid JSON.")
            raise

    def should_ignore(self, path: str) -> bool:
        """
        Check if a path should be ignored based on the ignore patterns.
        Uses glob pattern matching (e.g., *, **, ?, [seq], [!seq]).

        Args:
            path: The path to check against ignore patterns

        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        path = str(Path(path))  # Normalize path separators
        return any(
            fnmatch.fnmatch(name=path, pattern=pattern)
            for pattern in self.ignore_patterns
        )

    def create_directory(self, path: str) -> bool:
        """
        Create a directory if it's not in the ignore list.

        Args:
            path: The directory path to create

        Returns:
            bool: True if directory was created or exists, False if ignored
        """
        path: Path = Path(path)
        should_ignore = self.should_ignore(str(path))
        if should_ignore:
            click.echo(f"Skipping ignored directory: {path}")
            return False

        # If directory already exists, just check if it's ignored
        if path.exists():
            return not should_ignore

        # Check if parent directory exists and can be created if needed
        parent = path.parent
        if not parent.exists() and not self.create_directory(str(parent)):
            return False

        # Create the directory since parent exists and is not ignored
        path.mkdir(exist_ok=True)
        return True

    def write(self, path: str, content: str, mode: str = "w") -> bool:
        """
        Write content to a file if it's not in the ignore list.

        Args:
            path: The path where to write the file
            content: The content to write
            mode: The file opening mode (default: "w")

        Returns:
            bool: True if file was written, False if ignored
        """
        if self.should_ignore(path):
            click.echo(f"Skipping ignored path: {path}")
            return False

        # Create parent directories if they don't exist
        parent = Path(path).parent
        if not self.create_directory(str(parent)):
            return False

        # Write the file
        with open(path, mode) as f:
            f.write(content)
        return True

    def generate_python_models(
        self, models_dir: str, models_file_path: str, openapi_input: str
    ) -> bool:
        """
        Generate Python models using datamodel-codegen.

        Args:
            models_dir: Directory where models should be generated
            models_file_path: Path to the generated models file
            openapi_input: Path or URL to the OpenAPI spec

        Returns:
            bool: True if models were generated, False if ignored
        """
        if self.should_ignore(models_dir):
            click.echo(f"Skipping model generation: {models_dir} is ignored")
            return False

        if not self.create_directory(models_dir):
            return False

        models_path = Path(models_dir) / models_file_path
        if self.should_ignore(str(models_path)):
            click.echo(f"Skipping model generation: {models_path} is ignored")
            return False

        import subprocess

        cmd = [
            "datamodel-codegen",
            "--input-file-type",
            "openapi",
            "--input",
            str(openapi_input),
            "--output",
            str(models_path),
            "--use-standard-collections",
            "--use-schema-description",
            "--field-constraints",
            "--strict-nullable",
            "--wrap-string-literal",
            "--enum-field-as-literal",
            "one",
            "--use-double-quotes",
            "--use-default-kwarg",
            "--use-annotated",
            "--use-field-description",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--disable-timestamp",
        ]

        # Add --url flag if input is a URL
        if openapi_input.startswith(("http://", "https://")):
            cmd.extend(["--url", str(openapi_input)])

        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError as e:
            click.echo(f"Error generating models: {e}")
            return False

    @classmethod
    def from_click_context(
        cls, config: Optional[str] = None
    ) -> "ConfigurableFileWriter":
        """
        Create a FileWriter instance from Click context.

        Args:
            config: Optional path to the config file

        Returns:
            ConfigurableFileWriter: A new instance of the file writer
        """
        return cls(config_path=config)
