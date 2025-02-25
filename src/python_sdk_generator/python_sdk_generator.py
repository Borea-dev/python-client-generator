import re
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import click
import black
from jinja2 import Environment, FileSystemLoader

from ..content_loader import ContentLoader

from .models.borea_config_models import BoreaConfig
from .config_parser import ConfigParser

from .models.schema_model import SchemaPyJinja
from .models.sdk_class_models import (
    SdkClassPyJinja,
    OpenAPITagMetadata,
)
from .models.tag_class_models import TagClassPyJinja, OperationMetadata
from .models.handler_class_models import (
    HandlerClassPyJinja,
    HandlerClassPyJinja,
    MethodParameter,
)
from .file_writer import ConfigurableFileWriter
from ..openapi_parser.openapi_parser import OpenAPIParser
from ..openapi_parser.models import (
    HttpParameter,
    OpenAPIMetadata,
    Operation,
    SchemaMetadata,
)


class SDKGenerator:
    def __init__(
        self,
        metadata: OpenAPIMetadata,
        output_dir: Path,
        models_dir: Path,
        generate_tests: bool = True,
        config_path: Optional[str] = None,
    ):
        self.metadata = metadata
        self.output_dir = output_dir
        self.models_dir = models_dir
        self.generate_tests = generate_tests
        self.template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self.file_writer = ConfigurableFileWriter(config_path)

    def _clean_lower(self, tag: str) -> str:
        """Clean tag name to be a valid Python identifier"""
        return self._sanitize_string(tag).lower().replace(" ", "_").replace("-", "_")

    def _clean_capitalize(self, name: str) -> str:
        """Clean name to be a valid Python identifier"""
        # Remove spaces and dashes, convert to camel case
        name = self._sanitize_string(name)
        words = name.split("_")
        return "".join(word if word.isupper() else word.capitalize() for word in words)

    def _clean_parameter_name(self, name: str) -> str:
        """Clean parameter name to be a valid Python identifier"""
        # Convert hyphens to underscores
        return self._sanitize_string(name).replace("-", "_").replace(" ", "_").lower()

    def _clean_type_name(self, type_name: str) -> str:
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

    def _clean_file_name(self, name: str) -> str:
        """Clean name to be a valid file name"""
        # Convert to snake case
        name = name.replace("-", " ")
        words = name.split()
        return "_".join(word.lower() for word in words)

    def _clean_schema_name(self, name: str) -> str:
        """Clean name to be a valid Python identifier"""
        return name.replace("-", "_").replace(" ", "_")

    def _replace_dashes_with_underscores(self, name: str) -> str:
        """Replace dashes with underscores"""
        return name.replace("-", "_")

    def _replace_spaces_with_underscores(self, name: str) -> str:
        """Replace spaces with underscores"""
        return name.replace(" ", "_")

    def _format_description(self, description: str) -> str:
        """Format description to be a valid Python docstring"""
        return (
            description.replace("\\t", "")
            .replace("\\n", "")
            .replace("\\r", "")
            .replace('"', "'")
        )

    def _sanitize_string(self, s: str) -> str:
        # Replace common delimiters with underscore
        s = re.sub(r"[-/.,|:; ]", "_", s)
        # Remove all other special characters (keeping alphanumerics and underscores)
        s = re.sub(r"[^\w]", "", s)
        return s

    def _get_tag_formats(self, tag: str) -> Tuple[str, str, str]:
        tag_dir = self._clean_lower(tag)
        tag_class_name = self._clean_capitalize(tag)
        tag_filename = tag_dir
        return tag_dir, tag_class_name, tag_filename

    def _group_operations_by_tag(
        self,
    ) -> Tuple[Dict[str, List[Operation]], Dict[str, OpenAPITagMetadata]]:
        """Group operations by their tags"""
        operations_by_tag: Dict[str, List[Operation]] = {}
        tag_metadata_by_tag: Dict[str, OpenAPITagMetadata] = {}
        for op in self.metadata.operations:
            tag = op.tag
            tag_lowered = self._clean_lower(tag)
            if tag_lowered not in operations_by_tag:
                operations_by_tag[tag_lowered] = []
            operations_by_tag[tag_lowered].append(op)

            tag_capitalized = self._clean_capitalize(tag)
            tag_filename = tag_lowered + "_handler"

            tag_metadata_by_tag[tag_lowered] = OpenAPITagMetadata(
                tag=tag,
                tag_dir=tag_lowered,
                tag_filename=tag_filename,
                tag_class_name=tag_capitalized,
                tag_prop_name=tag_lowered,
                tag_description="",
            )

        return operations_by_tag, tag_metadata_by_tag

    def _generate_models(self):
        """Generate Pydantic models using datamodel-code-generator"""

    def format_type(self, type_info: Union[Dict, str, None]) -> str:
        resolved_type: str = "Any"
        if type_info is None:
            pass
        elif isinstance(type_info, str) and type_info not in ["object", "array"]:
            resolved_type = self._clean_type_name(type_info)
        elif isinstance(type_info, dict):
            if "$ref" in type_info:
                resolved_type = type_info["$ref"].split("/")[-1]
            elif type_info.get("type") == "array":
                resolved_type = f"List[{self.format_type(type_info.get('items', {}))}]"
            elif "type" in type_info and type_info["type"] not in ["object", "array"]:
                resolved_type = self._clean_type_name(type_info["type"])
            elif "allOf" in type_info:
                # TODO fix this when it hits
                # not hitting...
                resolved_type = " & ".join(
                    (
                        self.format_type(item)
                        if isinstance(item, dict) and "$ref" not in item
                        else item["$ref"].split("/")[-1]
                    )
                    for item in type_info["allOf"]
                )
            elif "oneOf" in type_info:
                # not hitting...
                resolved_type = f"Union[{', '.join(self.format_type(item) for item in type_info['oneOf'])}]"
            elif "anyOf" in type_info:
                # not hitting...
                resolved_type = f"Union[{', '.join(self.format_type(item) for item in type_info['anyOf'])}]"
            elif "not" in type_info:
                # not hitting...
                resolved_type = "Any"
            else:
                pass
        else:
            pass

        return resolved_type

    def _get_single_nested_schema(
        self, schema: Union[SchemaMetadata, None]
    ) -> Union[Dict[str, Any], None]:
        if schema is None:
            return None
        if schema.length_nested_json_schemas != 1:
            return schema.model_dump()
        schema = schema.model_dump()
        nested_schema = schema.get("nested_json_schemas", [None])[0]
        if nested_schema:
            return nested_schema
        return schema

    def _method_params_from_http_params(
        self, http_params: List[HttpParameter], cond: Callable[[HttpParameter], bool]
    ) -> List[MethodParameter]:
        """
        Returns a list of MethodParameter objects based on the given condition.
        """
        return [
            MethodParameter(
                required=http_param.required,
                name=http_param.name,
                original_name=http_param.original_name,
                type=self.format_type(http_param.type),
                description=http_param.description,
            )
            for http_param in http_params
            if cond(http_param)
        ]

    def _method_params_from_schema_props(
        self,
        schema: Dict[str, Any],
        props: List[Dict[str, Any]],
        cond: Callable[[str, bool], bool],
    ) -> List[MethodParameter]:
        default_description = "No description provided"
        schema_required = schema.get("required", [])
        is_required = lambda prop_name, prop: prop_name in schema_required or prop.get(
            "required", False
        )
        return [
            MethodParameter(
                required=is_required(prop_name, prop),
                name=prop_name,
                type=self.format_type(prop),
                description=prop.get("description", None)
                or prop.get("nested_json_schemas", [schema])[0].get("description", None)
                or default_description,
            )
            for prop_name, prop in props.items()
            if cond(prop_name, is_required(prop_name, prop))
        ]

    def _method_param_from_request_body(
        self, request_body: Dict[str, Any]
    ) -> List[MethodParameter]:
        return [
            MethodParameter(
                required=request_body.get("required", False),
                name="request_body",
                type=self.format_type(request_body.get("type", None)),
                description=request_body.get("description", "Request body"),
            )
        ]

    def _resolve_method_params(
        self, operation: Operation, schema: Union[Dict[str, Any], None]
    ) -> Tuple[List[MethodParameter], List[MethodParameter]]:
        required_http_params: List[MethodParameter] = (
            self._method_params_from_http_params(
                operation.parameters, lambda http_param: http_param.required == True
            )
        )
        optional_http_params: List[MethodParameter] = (
            self._method_params_from_http_params(
                operation.parameters, lambda http_param: http_param.required != True
            )
        )
        http_param_names = [param.name for param in operation.parameters]

        required_schema_props: List[MethodParameter] = []
        optional_schema_props: List[MethodParameter] = []
        if schema is not None:
            schema_props = schema.get("properties", None)
            if schema_props:
                required_schema_props += self._method_params_from_schema_props(
                    schema,
                    schema_props,
                    lambda prop_name, is_required: is_required
                    and prop_name not in http_param_names,
                )
                optional_schema_props += self._method_params_from_schema_props(
                    schema,
                    schema_props,
                    lambda prop_name, is_required: not is_required
                    and prop_name not in http_param_names,
                )
            elif schema.get("required", False):
                required_schema_props += self._method_param_from_request_body(schema)
            else:
                optional_schema_props += self._method_param_from_request_body(schema)

        required_method_params = required_http_params + required_schema_props
        optional_method_params = optional_http_params + optional_schema_props

        return [required_method_params, optional_method_params]

    def _generate_handler_class(
        self,
        operation: Operation,
        parent_class_name: str,
        parent_filename: str,
        operation_metadata: OperationMetadata,
    ) -> str:
        """Generate the handler for a specific path / operation in OpenAPI"""
        op = operation

        for param in op.parameters:
            # Add original name for query parameters
            param.original_name = param.name
            param.name = self._clean_parameter_name(param.name)
            param.type = self._clean_type_name(param.type)
        if op.request_body and isinstance(op.request_body, SchemaMetadata):
            op.request_body.type = self._clean_type_name(op.request_body.type)

        http_params = op.parameters
        request_body = op.request_body
        schema: Union[Dict[str, Any], None] = self._get_single_nested_schema(
            op.request_body
        )
        required_method_params, optional_method_params = self._resolve_method_params(
            operation=operation, schema=schema
        )
        handler_metadata = HandlerClassPyJinja(
            parent_class_name=parent_class_name,
            parent_filename=parent_filename,
            class_name=operation_metadata.handler_class_name,
            method_name=operation_metadata.handler_filename,
            description=op.description,
            required_method_params=required_method_params,
            optional_method_params=optional_method_params,
            http_method=op.method.upper(),
            path=op.path,
            http_params=http_params,
            request_body=request_body,
            nested_schema=schema,
        ).model_dump()

        return self._render_template_and_format_code(
            "handler_class.py.jinja", template_metadata=handler_metadata
        )

    def _generate_tag_class(
        self,
        parent_class_name: str,
        sdk_class_filename: str,
        tag_class_name: str,
        tag_description: str,
        operation_metadata: List[OperationMetadata],
    ) -> str:
        template_metadata = TagClassPyJinja(
            parent_class_name=parent_class_name,
            parent_filename=sdk_class_filename,
            class_name=tag_class_name,
            description=tag_description,
            operation_metadata=operation_metadata,
        ).model_dump()

        return self._render_template_and_format_code(
            "tag_class.py.jinja", template_metadata=template_metadata
        )

    def _generate_sdk_class(
        self, parent_class_name: str, tag_metadata: List[OpenAPITagMetadata]
    ) -> str:
        """Generate the base class for methods of tag in OpenAPI"""
        base_url = self.metadata.servers and self.metadata.servers[0].url or ""
        http_headers = self.metadata.headers
        template_metadata = SdkClassPyJinja(
            class_name=parent_class_name,
            class_title=self.metadata.info.title,
            class_description=self.metadata.info.description,
            base_url=base_url,
            http_headers=http_headers,
            tags=tag_metadata,
        ).model_dump()

        return self._render_template_and_format_code(
            "sdk_class.py.jinja", template_metadata=template_metadata
        )

    def _generate_schema_files(self, models_filename: str, file_ext: str) -> None:
        """Generate individual schema files for each component in the models_output directory."""
        self.file_writer.create_directory(str(self.models_dir))

        schemas = {
            **self.metadata.components.schemas,
            # **self.metadata.components.securitySchemes,
        }

        for schema_name, schema_data in schemas.items():
            file_name = self._clean_schema_name(schema_name) + file_ext
            file_path = self.models_dir / file_name
            description = schema_data.get("description", "")
            description = self._format_description(description)

            template_metadata = SchemaPyJinja(
                schema_name=schema_name,
                schema_data=schema_data,
                models_filename=models_filename,
                description=description,
            ).model_dump()

            rendered_code = self._render_template_and_format_code(
                "schema.py.jinja", template_metadata=template_metadata
            )
            self.file_writer.write(str(file_path), rendered_code)

    def _generate_requirements(self) -> str:
        """Generate requirements.txt with required dependencies using a template"""
        from datetime import datetime

        template_metadata = {
            "package_name": self.metadata.info.title,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return self._render_template_and_format_code(
            "requirements.txt.jinja",
            template_metadata=template_metadata,
            format_with_black=False,
        )

    def _render_template_and_format_code(
        self,
        template_name: str,
        template_metadata: Dict[str, Any],
        format_with_black: bool = True,
    ) -> str:
        template = self.env.get_template(template_name)
        try:
            rendered_code = template.render(template_metadata)
        except Exception as e:
            click.echo(template_metadata)
            raise e

        if format_with_black:
            try:
                formatted_code = black.format_str(rendered_code, mode=black.Mode())
            except Exception as e:
                click.echo(rendered_code)
                raise e
            return formatted_code
        else:
            return rendered_code

    def _generate_tests(self, tag: str, operations: List[Operation]) -> str:
        """Generate tests for a specific tag"""
        template = self.env.get_template("test_client.py.jinja")
        template_metadata = {
            "tag": tag,
            "operations": operations,
            "class_name": self._clean_capitalize(tag),
            "metadata": self.metadata,
        }
        return self._render_template_and_format_code(
            "test_client.py.jinja", template_metadata=template_metadata
        )

    def _generate_readme(self, operations_by_tag: Dict[str, List[Operation]]) -> str:
        """Generate README.md with SDK documentation"""
        template_metadata = {
            "metadata": self.metadata,
            "operations_by_tag": operations_by_tag,
        }
        return self._render_template_and_format_code(
            "README.md.jinja",
            template_metadata=template_metadata,
            format_with_black=False,
        )

    def _get_tag_description(self, tag: str) -> Union[str, None]:
        for t in self.metadata.tags:
            if t == tag:
                return t.description
        return None

    def generate(self) -> None:
        """Generate the SDK."""
        # Shared SDK class / file vars
        file_ext = ".py"
        parent_class_name = self._clean_capitalize(self.metadata.info.title)
        sdk_class_filename = self._clean_file_name(self.metadata.info.title)

        # Create output directories
        self.file_writer.create_directory(str(self.output_dir) or sdk_class_filename)

        # Generate models
        openapi_input = self.metadata.openapi_input
        models_filename = "models"
        models_file_path = models_filename + file_ext
        self.file_writer.generate_python_models(
            models_dir=str(self.models_dir),
            models_file_path=models_file_path,
            openapi_input=openapi_input,
        )

        # Generate schema files
        self._generate_schema_files(models_filename=models_filename, file_ext=file_ext)

        # Generate src directory if needed
        src_dir = self.output_dir / "src"
        self.file_writer.create_directory(str(src_dir))

        # Generate test directory if needed
        test_dir = self.output_dir / "tests"
        if self.generate_tests:
            self.file_writer.create_directory(str(test_dir))

        # Generate handlers (tag/<operation_id>/<operation_id>.py)
        operation_metadata_by_tag: Dict[str, List[OperationMetadata]] = {}
        for op in self.metadata.operations:
            tag_name = op.tag
            tag_dir, tag_class_name, tag_filename = self._get_tag_formats(tag_name)
            tag_dir_path = src_dir / tag_dir
            handler_filename = op.operation_id
            handler_dir = handler_filename
            handler_file_dir_path = tag_dir_path / handler_dir
            self.file_writer.create_directory(str(handler_file_dir_path))
            handler_file = handler_filename + file_ext
            handler_file_path = handler_file_dir_path / handler_file
            handler_class_name = self._clean_capitalize(handler_filename)
            operation_metadata = OperationMetadata(
                handler_dir=handler_dir,
                handler_filename=handler_filename,
                handler_class_name=handler_class_name,
            )
            operation_handler_content = self._generate_handler_class(
                op, parent_class_name, sdk_class_filename, operation_metadata
            )
            self.file_writer.write(str(handler_file_path), operation_handler_content)
            if tag_name not in operation_metadata_by_tag:
                operation_metadata_by_tag[tag_name] = []
            operation_metadata_by_tag[tag_name].append(operation_metadata)

            # TODO: not implemented
            # Generate tests
            if self.generate_tests:
                tag_test_dir_path = test_dir / tag_dir
                handler_test_file_dir_path = tag_test_dir_path / handler_filename
                self.file_writer.create_directory(str(handler_test_file_dir_path))
                handler_test_file = handler_filename + "_test" + file_ext
                handler_test_file_path = handler_test_file_dir_path / handler_test_file
                test_content = ""
                # test_content = self._generate_tests(tag, operations)
                self.file_writer.write(str(handler_test_file_path), test_content)

        tag_metadata: List[OpenAPITagMetadata] = []
        for tag in self.metadata.tags:
            tag_name = tag.name
            if tag_name not in operation_metadata_by_tag:
                continue
            tag_description = tag.description
            tag_dir, tag_class_name, tag_filename = self._get_tag_formats(tag_name)
            operation_metadata = operation_metadata_by_tag[tag_name]
            tag_dir_path = src_dir / tag_dir
            tag_test_dir_path = test_dir / tag_dir
            self.file_writer.create_directory(str(tag_dir_path))
            tag_file = tag_filename + file_ext
            tag_file_path = tag_dir_path / tag_file
            tag_class_content = self._generate_tag_class(
                parent_class_name,
                sdk_class_filename,
                tag_class_name,
                tag_description,
                operation_metadata,
            )
            self.file_writer.write(str(tag_file_path), tag_class_content)
            tag_metadata.append(
                OpenAPITagMetadata(
                    tag=tag_name,
                    tag_description=tag_description,
                    tag_dir=tag_dir,
                    tag_filename=tag_filename,
                    tag_class_name=tag_class_name,
                    tag_prop_name=tag_dir,
                )
            )

            if self.generate_tests:
                self.file_writer.create_directory(str(tag_test_dir_path))

        # Generate base client
        sdk_class_file = sdk_class_filename + file_ext
        sdk_class_file_path = src_dir / sdk_class_file
        sdk_class_content = self._generate_sdk_class(
            parent_class_name=parent_class_name, tag_metadata=tag_metadata
        )
        self.file_writer.write(str(sdk_class_file_path), sdk_class_content)

        # Generate requirements.txt
        requirements_path = self.output_dir / "requirements.txt"
        requirements_content = self._generate_requirements()
        self.file_writer.write(str(requirements_path), requirements_content)

        # TODO: needs to be re-implemented
        # Generate README
        readme_path = self.output_dir / "README.md"
        # readme_content = self._generate_readme(operations_by_tag)
        # self.file_writer.write(str(readme_path), readme_content)

        # Load openapi.json
        openapi_file = self.output_dir / "openapi.json"
        content_loader = ContentLoader()
        openapi_content = content_loader.load_json(self.metadata.openapi_input)
        self.file_writer.write(str(openapi_file), json.dumps(openapi_content, indent=2))


def load_config(config_path: str = "borea.config.json") -> Dict[str, Any]:
    """Load configuration from borea.config.json"""
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


@click.command()
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
    "--config",
    "-c",
    help="Path to borea.config.json",
    type=str,
)
def main(
    openapi_input: Optional[str],
    sdk_output: Optional[str],
    models_output: Optional[str],
    tests: Optional[bool],
    config: Optional[str],
):
    """Generate a Python SDK from an OpenAPI specification.

    The OpenAPI specification can be provided as a local file path or a URL.
    For URLs, both JSON and YAML formats are supported.
    """
    # Default values
    default_config = "borea.config.json"
    default_input = "openapi.json"
    default_sdk_output = "generated_sdk"
    default_models_dir = "models"
    default_tests = False

    # Load borea config
    borea_config: BoreaConfig = ConfigParser.from_source(config, default_config)

    # Use defaults if CLI args OR config values are not provided
    openapi_input = openapi_input or borea_config.input.openapi or default_input
    sdk_output_path = Path(
        sdk_output or borea_config.output.clientSDK or default_sdk_output
    )
    models_output_path = Path(
        sdk_output_path
        / (models_output or borea_config.output.models or default_models_dir)
    )
    tests = tests or borea_config.output.tests or default_tests

    parser = OpenAPIParser(openapi_input)
    metadata = parser.parse()

    generator = SDKGenerator(
        metadata=metadata,
        output_dir=sdk_output_path,
        models_dir=models_output_path,
        generate_tests=tests,
        config_path=config,
    )
    generator.generate()

    click.echo(f"Successfully generated SDK in: {sdk_output_path}")


if __name__ == "__main__":
    main()
