import re
from typing import Dict, Union

import click


class Helpers:
    @classmethod
    def sanitize_string(cls, s: str) -> str:
        # Replace common delimiters with underscore
        s = re.sub(r"[-/.,|:; ]", "_", s)
        # Remove all other special characters (keeping alphanumerics and underscores)
        s = re.sub(r"[^\w]", "", s)
        return s

    @classmethod
    def clean_lower(cls, tag: str) -> str:
        """Clean tag name to be a valid Python identifier"""
        return cls.sanitize_string(tag).lower().replace(" ", "_").replace("-", "_")

    @classmethod
    def clean_capitalize(cls, name: str) -> str:
        """Clean name to be a valid Python identifier"""
        # Remove spaces and dashes, convert to camel case
        name = cls.sanitize_string(name)
        words = name.split("_")
        return "".join(word if word.isupper() else word.capitalize() for word in words)

    @classmethod
    def clean_parameter_name(cls, name: str) -> str:
        """Clean parameter name to be a valid Python identifier"""
        # Convert hyphens to underscores
        return cls.sanitize_string(name).replace("-", "_").replace(" ", "_").lower()

    @classmethod
    def clean_type_name(cls, type_name: str) -> str:
        """Clean type name to be a valid Python type"""
        if "int" in type_name:
            return "int"
        type_map = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "number": "float",
            "array": "List",
            "object": "Dict[str, Any]",
        }
        return type_map.get(type_name.lower(), type_name)

    @classmethod
    def clean_file_name(cls, name: str) -> str:
        """Clean name to be a valid file name"""
        # Convert to snake case
        name = name.replace("-", " ")
        words = name.split()
        return "_".join(word.lower() for word in words)

    @classmethod
    def clean_schema_name(cls, name: str) -> str:
        """Clean name to be a valid Python identifier"""
        return name.replace("-", "_").replace(" ", "_")

    @classmethod
    def replace_dashes_with_underscores(cls, name: str) -> str:
        """Replace dashes with underscores"""
        return name.replace("-", "_")

    @classmethod
    def replace_spaces_with_underscores(cls, name: str) -> str:
        """Replace spaces with underscores"""
        return name.replace(" ", "_")

    @classmethod
    def format_description(cls, description: str) -> str:
        """Format description to be a valid Python docstring"""
        return (
            description.replace("\\t", "")
            .replace("\\n", "")
            .replace("\\r", "")
            .replace('"', "'")
        )

    @classmethod
    def format_type(cls, type_info: Union[Dict, str, None]) -> str:
        resolved_type: str = "Any"
        if type_info is None:
            pass
        elif isinstance(type_info, str) and type_info not in ["object", "array"]:
            resolved_type = cls.clean_type_name(type_info)
        elif isinstance(type_info, dict):
            if "$ref" in type_info:
                resolved_type = type_info["$ref"].split("/")[-1]
            elif type_info.get("type") == "array":
                resolved_type = f"List[{cls.format_type(type_info.get('items', {}))}]"
            elif "type" in type_info and type_info["type"] not in ["object", "array"]:
                resolved_type = cls.clean_type_name(type_info["type"])
            elif "allOf" in type_info:
                # TODO fix this when it hits
                # not hitting...
                resolved_type = " & ".join(
                    (
                        cls.format_type(item)
                        if isinstance(item, dict) and "$ref" not in item
                        else item["$ref"].split("/")[-1]
                    )
                    for item in type_info["allOf"]
                )
            elif "oneOf" in type_info:
                # not hitting...
                resolved_type = f"Union[{', '.join(cls.format_type(item) for item in type_info['oneOf'])}]"
            elif "anyOf" in type_info:
                # not hitting...
                resolved_type = f"Union[{', '.join(cls.format_type(item) for item in type_info['anyOf'])}]"
            elif "not" in type_info:
                # not hitting...
                resolved_type = "Any"
            else:
                pass
        else:
            pass

        return resolved_type

    @staticmethod
    def run_ruff_on_path(path: str):
        import subprocess

        def ruff(command: str, path: str):
            subprocess.run(
                ["ruff", command, path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        try:
            # Run ruff check (linting)
            # ruff("check", file_path)

            # Run ruff format (formatting)
            ruff("format", path)

        except subprocess.CalledProcessError as e:
            click.echo(f"Error running ruff: {e}")
