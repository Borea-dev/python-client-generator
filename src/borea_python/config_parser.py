from typing import List, Optional

import click

from .content_loader import ContentLoader, ContentLoadError
from .models.borea_config_models import (
    BoreaConfig,
    BoreaConfigJSON,
    InputConfig,
    InputConfigJSON,
    OutputConfig,
)
from .path_validator import PathValidator


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class ConfigParser:
    """Parser for Borea configuration that handles resolution of List[str] inputs."""

    def __init__(self):
        """Initialize the ConfigParser with a ContentLoader."""
        self.content_loader = ContentLoader()

    @staticmethod
    def resolve_path(paths: List[str], purpose: str) -> str:
        """
        Try to resolve a path from a list of possible paths.

        Args:
            paths: List of paths to try (can be file paths or URLs)
            purpose: Description of what this path is for (used in error messages)

        Returns:
            str: The first working path

        Raises:
            ConfigError: If no paths work
        """
        validator = PathValidator()
        for path in paths:
            is_valid, path_type, error = validator.validate(path)
            if is_valid:
                return path

        paths_str = "\n  ".join(paths)
        raise ConfigError(
            f"Could not resolve {purpose} from any of these paths:\n  {paths_str}"
        )

    @staticmethod
    def get_default_config() -> BoreaConfig:
        """Return a default BoreaConfig with empty/None values."""
        return BoreaConfig()

    @classmethod
    def parse_input_config(cls, input: InputConfigJSON) -> InputConfig:
        """
        Parse and validate an InputConfigJSON, resolving all List[str] fields.

        Args:
            input: The InputConfigJSON to parse

        Returns:
            InputConfig: A new input config with resolved path

        Raises:
            ConfigError: If all paths cannot be resolved
        """
        return InputConfig(openapi=cls.resolve_path(input.openapi, "OpenAPI spec"))

    @classmethod
    def parse_output_config(cls, output: OutputConfig) -> OutputConfig:
        """
        Parse and validate an OutputConfig.

        Args:
            output: The OutputConfig to parse

        Returns:
            OutputConfig: A new output config
        """
        return OutputConfig(**output.model_dump())

    @classmethod
    def parse_config(cls, config: BoreaConfigJSON) -> BoreaConfig:
        """
        Parse and validate a BoreaConfig, resolving all paths.

        Args:
            config: The BoreaConfig to parse

        Returns:
            BoreaConfig: A new config with resolved paths

        Raises:
            ConfigError: If any required paths cannot be resolved
        """
        return BoreaConfig(
            input=cls.parse_input_config(config.input),
            output=cls.parse_output_config(config.output),
            ignores=config.ignores,  # Keep ignores as is since they're glob patterns
        )

    @staticmethod
    def log_warning_default_config_not_found() -> None:
        """Log a warning message when the default config is not found."""
        click.echo(
            "Warning: No borea.config.json found. Command line arguments or defaults will be used."
        )

    @classmethod
    def load_config_from_source(
        cls, source: str, is_default: bool = False
    ) -> Optional[dict]:
        """
        Load configuration data from either a local file or URL.

        Args:
            source: Path to local file or URL
            is_default: Whether this is loading the default config file

        Returns:
            Optional[dict]: Loaded configuration data, or None if source doesn't exist and is_default=True

        Raises:
            ConfigError: If the config cannot be loaded/parsed, or if a non-default config doesn't exist
        """
        try:
            content_loader = ContentLoader()
            return content_loader.load_json(source)
        except ContentLoadError as e:
            if is_default:
                cls.log_warning_default_config_not_found()
                return None
            raise ConfigError(str(e))
        except Exception as e:
            raise ConfigError(f"Error loading config from {source}: {str(e)}")

    @classmethod
    def from_source(cls, source: str, default_source: str) -> BoreaConfig:
        """
        Create a BoreaConfig from either a local file or URL.
        If the user provided source it loads it or fails to.
        Otherwise it loads the default source if it exists.

        Args:
            source: Path to local file or URL containing the configuration
            default_source: Path to default config file

        Returns:
            BoreaConfig: Parsed and validated configuration

        Raises:
            ConfigError: If the user config exists but cannot be loaded, parsed, or validated
        """
        source = source or default_source
        is_default = bool(source)
        config_data = cls.load_config_from_source(source, is_default=is_default)

        if config_data is not None:
            try:
                # First validate against BoreaConfigJSON model
                json_config = BoreaConfigJSON.model_validate(config_data)
                # Then parse and convert to BoreaConfig model
                parsed_config: BoreaConfig = cls.parse_config(json_config)
                return parsed_config
            except Exception as e:
                raise ConfigError(f"Failed to validate config: {str(e)}")

        return cls.get_default_config()
