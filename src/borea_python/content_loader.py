"""Module for handling content loading from URLs and files."""

import json
from typing import Any, Dict
from urllib.request import urlopen

import yaml

from .path_validator import PathValidator


class ContentLoadError(Exception):
    """Exception raised for content loading errors."""

    pass


class ContentLoader:
    """Class to handle loading content from URLs or files and writing data to files."""

    def __init__(self):
        """Initialize the ContentLoader with a PathValidator."""
        self.validator = PathValidator()

    def load_content(self, path: str, encoding: str = "utf-8") -> str:
        """
        Load content from a URL or file path.

        Args:
            path: URL or file path to load content from
            encoding: Character encoding to use when reading content (default: utf-8)

        Returns:
            str: The loaded content

        Raises:
            ContentLoadError: If the content cannot be loaded
        """
        is_valid, path_type, error = self.validator.validate(path)
        if not is_valid:
            raise ContentLoadError(f"Invalid path: {error}")

        try:
            if path_type == "url":
                with urlopen(path, timeout=5) as response:
                    return response.read().decode(encoding)
            else:  # path_type == "file"
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
        except Exception as e:
            raise ContentLoadError(f"Failed to load content from {path}: {str(e)}")

    def load_structured_data(self, path: str) -> Dict[str, Any]:
        """
        Load and parse structured data (JSON or YAML) from a URL or file path.

        Args:
            path: URL or file path to load data from

        Returns:
            Any: The parsed data structure

        Raises:
            ContentLoadError: If the content cannot be loaded or parsed as JSON/YAML
        """
        content = self.load_content(path)

        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # If JSON fails, try YAML
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise ContentLoadError(
                    f"Content from {path} is neither valid JSON nor YAML: {str(e)}"
                )

    def load_json(self, path: str) -> Dict[str, Any]:
        """
        Load and parse JSON content from a URL or file path.

        Args:
            path: URL or file path to load JSON from

        Returns:
            Any: The parsed JSON content

        Raises:
            ContentLoadError: If the content cannot be loaded or parsed as JSON
        """
        content = self.load_content(path)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ContentLoadError(f"Invalid JSON in {path}: {str(e)}")

    def load_yaml(self, path: str) -> Any:
        """
        Load and parse YAML content from a URL or file path.

        Args:
            path: URL or file path to load YAML from

        Returns:
            Any: The parsed YAML content

        Raises:
            ContentLoadError: If the content cannot be loaded or parsed as YAML
        """
        content = self.load_content(path)
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ContentLoadError(f"Invalid YAML in {path}: {str(e)}")
