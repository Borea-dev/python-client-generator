"""Module for validating URLs and file paths."""

import os
from typing import Tuple, Union
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen


class PathValidator:
    """Class to validate if a string is a valid URL or file path."""

    @staticmethod
    def validate(path: str) -> Tuple[bool, str, Union[str, None]]:
        """
        Validate if the input string is a valid URL or file path.

        Args:
            path: String to validate

        Returns:
            Tuple containing:
            - bool: True if valid, False otherwise
            - str: Type of path ('url' or 'file')
            - Union[str, None]: Error message if invalid, None if valid
        """
        if not path:
            return False, "", "Empty path provided"

        # First try as URL
        try:
            result = urlparse(path)
            if all([result.scheme, result.netloc]):
                # Valid URL format, now check if it's accessible
                try:
                    with urlopen(path, timeout=5) as response:
                        if response.status == 200:
                            return True, "url", None
                        return (
                            False,
                            "url",
                            f"URL returned status code: {response.status}",
                        )
                except URLError as e:
                    return False, "url", f"URL is not accessible: {str(e)}"
                except TimeoutError:
                    return False, "url", "URL request timed out"
        except ValueError:
            pass

        # Try as file path
        try:
            if os.path.exists(path):
                return True, "file", None
            else:
                return False, "file", "File does not exist"
        except Exception as e:
            return False, "file", f"Invalid file path: {str(e)}"

        return False, "", "Invalid URL or file path format"
