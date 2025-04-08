import re
from typing import Dict, Union

import click


class Helpers:
    @classmethod
    def sanitize_string(cls, s: str) -> str:
        """Replace dash, slash, period, comma, pipe, colon, semicolon, and space delimiters with underscore"""
        s = re.sub(r"[-/.,|:; ]", "_", s)
        # Remove all other special characters (keeping alphanumerics and underscores)
        s = re.sub(r"[^\w]", "", s)
        return s

    @classmethod
    def sanitize_and_lower_string(cls, s: str) -> str:
        return cls.sanitize_string(s).lower()

    @classmethod
    def clean_lower(cls, tag: str) -> str:
        """Clean tag name to be a valid Python identifier"""
        return cls.sanitize_and_lower_string(tag)

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
        return cls.sanitize_and_lower_string(name)

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
        return cls.sanitize_and_lower_string(name)

    @classmethod
    def clean_schema_name(cls, name: str) -> str:
        """Clean name to be a valid Python identifier"""
        return cls.sanitize_and_lower_string(name)

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
        schema_type: str = resolved_type
        type_is_schema: bool = False

        def set_schema_type_to_resolved_type(value: str):
            nonlocal resolved_type
            nonlocal schema_type
            resolved_type = value
            schema_type = value

        if type_info is None:
            pass
        elif isinstance(type_info, str) and type_info not in ["object", "array"]:
            set_schema_type_to_resolved_type(cls.clean_type_name(type_info))
        elif isinstance(type_info, dict):
            type_is_schema = type_info.get("type_is_schema", False)
            if "$ref" in type_info:
                set_schema_type_to_resolved_type(type_info["$ref"].split("/")[-1])
            elif type_info.get("type") == "array":
                items = type_info.get("items", {})
                items_type = cls.format_type(items)[0]
                resolved_type = f"List[{items_type}]"
                schema_type = items_type
                type_is_schema = items.get("type_is_schema", False)
            elif "type" in type_info and type_info["type"] not in ["object", "array"]:
                set_schema_type_to_resolved_type(cls.clean_type_name(type_info["type"]))
            elif "allOf" in type_info:
                # TODO fix this when it hits
                # not hitting...
                value = " & ".join(
                    (
                        cls.format_type(item)[0]
                        if isinstance(item, dict) and "$ref" not in item
                        else item["$ref"].split("/")[-1]
                    )
                    for item in type_info["allOf"]
                )
                set_schema_type_to_resolved_type(value)
            elif "oneOf" in type_info:
                # not hitting...
                value = f"Union[{', '.join(cls.format_type(item)[0] for item in type_info['oneOf'])}]"
                set_schema_type_to_resolved_type(value)
            elif "anyOf" in type_info:
                # not hitting...
                value = f"Union[{', '.join(cls.format_type(item)[0] for item in type_info['anyOf'])}]"
                set_schema_type_to_resolved_type(value)
            elif "not" in type_info:
                # not hitting...
                set_schema_type_to_resolved_type("Any")
            else:
                pass
        else:
            pass

        return [resolved_type, schema_type, type_is_schema]

    @staticmethod
    def run_ruff_on_path(path: str):
        import subprocess

        def ruff(*args: str):
            subprocess.run(
                ["ruff", *args],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        try:
            # TODO: get generated code good enough to be fixed
            # Run ruff check (linting)
            ruff("check", "--fix", path)

            # Run ruff format (formatting)
            ruff("format", path)

        except subprocess.CalledProcessError as e:
            click.echo(f"Error running ruff: {e}")
