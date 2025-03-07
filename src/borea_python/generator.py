import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import click
from jinja2 import Environment, FileSystemLoader

from .content_loader import ContentLoader
from .file_writer import ConfigurableFileWriter
from .generate_method_metadata import GenerateMethodMetadata
from .helpers import Helpers
from .models.borea_config_models import BoreaConfig
from .models.handler_class_models import (
    HandlerClassPyJinja,
)
from .models.openapi_models import (
    OpenAPIMetadata,
    Operation,
    SchemaMetadata,
)
from .models.schema_model import SchemaPyJinja
from .models.sdk_class_models import (
    OpenAPITagMetadata,
    SdkClassPyJinja,
)
from .models.tag_class_models import OperationMetadata, TagClassPyJinja
from .x_code_sample_generator import XCodeSampleGenerator


class SDKGenerator:
    def __init__(
        self,
        metadata: OpenAPIMetadata,
        output_dir: Path,
        models_dir: Path,
        generate_tests: bool,
        generate_x_code_samples: bool,
        borea_config: BoreaConfig,
    ):
        self.metadata = metadata
        self.output_dir = output_dir
        self.models_dir = models_dir
        self.generate_tests = generate_tests
        self.generate_x_code_samples = generate_x_code_samples
        self.template_dir = Path(__file__).parent / "templates"
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        self.file_writer = ConfigurableFileWriter(ignores=borea_config.ignores)

    @classmethod
    def _get_tag_formats(self, tag: str) -> Tuple[str, str, str]:
        tag_dir = Helpers.clean_lower(tag)
        tag_class_name = Helpers.clean_capitalize(tag)
        tag_filename = tag_dir
        return tag_dir, tag_class_name, tag_filename

    def _generate_models(self, models_dir: str, models_filename: str, file_ext: str):
        """Generate Pydantic models using datamodel-code-generator"""
        openapi_input = self.metadata.openapi_input
        models_file = models_filename + file_ext
        self.file_writer.generate_python_models(
            models_dir=models_dir,
            models_file=models_file,
            openapi_input=openapi_input,
        )

    def _generate_handler_class(
        self,
        operation: Operation,
        parent_class_name: str,
        parent_filename: str,
        is_operation_without_tag: bool,
        operation_metadata: OperationMetadata,
        models_dir: str,
        models_filename: str,
    ) -> str:
        """Generate the handler for a specific path / operation in OpenAPI"""
        op = operation

        for param in op.parameters:
            # Add original name for query parameters
            param.original_name = param.name
            param.name = Helpers.clean_parameter_name(param.name)
            param.type = Helpers.clean_type_name(param.type)
        if op.request_body and isinstance(op.request_body, SchemaMetadata):
            op.request_body.type = Helpers.clean_type_name(op.request_body.type)

        http_params = op.parameters
        request_body = op.request_body
        (
            schema,
            required_method_params,
            optional_method_params,
        ) = GenerateMethodMetadata.resolve_method_params(op.parameters, op.request_body)
        handler_metadata = HandlerClassPyJinja(
            models_dir=models_dir,
            models_filename=models_filename,
            parent_class_name=parent_class_name,
            parent_filename=parent_filename,
            is_operation_without_tag=is_operation_without_tag,
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

        return self._render_code(
            "handler_class.py.jinja", template_metadata=handler_metadata
        )

    def _generate_tag_class(
        self,
        parent_class_name: str,
        sdk_class_filename: str,
        tag_class_name: str,
        tag_description: str,
        operation_metadata: List[OperationMetadata],
        models_dir: str,
        models_filename: str,
    ) -> str:
        template_metadata = TagClassPyJinja(
            models_dir=models_dir,
            models_filename=models_filename,
            parent_class_name=parent_class_name,
            parent_filename=sdk_class_filename,
            class_name=tag_class_name,
            description=tag_description,
            operation_metadata=operation_metadata,
        ).model_dump()

        return self._render_code(
            "tag_class.py.jinja", template_metadata=template_metadata
        )

    def _generate_sdk_class(
        self,
        parent_class_name: str,
        tag_metadata: List[OpenAPITagMetadata],
        operations_without_tags: List[OperationMetadata],
        models_dir: str,
        models_filename: str,
    ) -> str:
        """Generate the base class for methods of tag in OpenAPI"""
        base_url = self.metadata.servers and self.metadata.servers[0].url or ""
        http_headers = self.metadata.headers
        template_metadata = SdkClassPyJinja(
            models_dir=models_dir,
            models_filename=models_filename,
            class_name=parent_class_name,
            class_title=self.metadata.info.title,
            class_description=self.metadata.info.description,
            base_url=base_url,
            http_headers=http_headers,
            tags=tag_metadata,
            operation_metadata=operations_without_tags,
        ).model_dump()

        return self._render_code(
            "sdk_class.py.jinja", template_metadata=template_metadata
        )

    def _generate_schema_files(self, models_filename: str, file_ext: str) -> None:
        """Generate individual schema files for each component in the models_output directory."""
        self._create_directory(str(self.models_dir))

        schemas = {
            **self.metadata.components.schemas,
            # **self.metadata.components.securitySchemes,
        }

        for schema_name, schema_data in schemas.items():
            file_name = Helpers.clean_schema_name(schema_name) + file_ext
            file_path = self.models_dir / file_name
            description = schema_data.get("description", "")
            description = Helpers.format_description(description)

            template_metadata = SchemaPyJinja(
                schema_name=schema_name,
                schema_data=schema_data,
                models_filename=models_filename,
                description=description,
            ).model_dump()

            rendered_code = self._render_code(
                "schema.py.jinja", template_metadata=template_metadata
            )
            self._write_and_format(str(file_path), rendered_code)

    def _generate_requirements(self) -> str:
        """Generate requirements.txt with required dependencies using a template"""
        from datetime import datetime

        template_metadata = {
            "package_name": self.metadata.info.title,
            "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return self._render_code(
            "requirements.txt.jinja",
            template_metadata=template_metadata,
        )

    def _generate_tests(self, tag: str, operations: List[Operation]) -> str:
        """Generate tests for a specific tag"""
        template_metadata = {
            "tag": tag,
            "operations": operations,
            "class_name": Helpers.clean_capitalize(tag),
            "metadata": self.metadata,
        }
        return self._render_code(
            "test_client.py.jinja", template_metadata=template_metadata
        )

    def _generate_readme(self, operations_by_tag: Dict[str, List[Operation]]) -> str:
        """Generate README.md with SDK documentation"""
        template_metadata = {
            "metadata": self.metadata,
            "operations_by_tag": operations_by_tag,
        }
        return self._render_code(
            "README.md.jinja",
            template_metadata=template_metadata,
        )

    def _generate_x_code_samples(
        self,
        openapi_content: Dict[str, Any],
        handler_file_paths_by_operation_id: Dict[str, str],
        file_ext: str,
    ) -> Dict[str, Any]:
        code_sample_generator = XCodeSampleGenerator(
            openapi_content=openapi_content,
            handler_file_paths_by_operation_id=handler_file_paths_by_operation_id,
            file_ext=file_ext,
        )
        openapi_content = code_sample_generator.add_code_samples()
        return openapi_content

    def _render_code(
        self,
        template_name: str,
        template_metadata: Dict[str, Any],
    ) -> str:
        template = self.env.get_template(template_name)
        try:
            rendered_code = template.render(template_metadata)
        except Exception as e:
            click.echo(template_metadata)
            raise e
        return rendered_code

    def _get_tag_description(self, tag: str) -> Union[str, None]:
        for t in self.metadata.tags:
            if t == tag:
                return t.description
        return None

    def _create_directory(self, dir_path: str) -> None:
        self.file_writer.create_directory(dir_path)
        self.file_writer.write(str(Path(dir_path) / "__init__.py"), "")

    def _write_and_format(self, file_path: str, file_content: str) -> None:
        self.file_writer.write(file_path, file_content)
        # Helpers.run_ruff_on_path(file_path)

    def generate(self) -> None:
        """Generate the SDK."""
        # Shared SDK class / file vars
        file_ext = ".py"
        parent_class_name = Helpers.clean_capitalize(self.metadata.info.title)
        sdk_class_filename = Helpers.clean_file_name(self.metadata.info.title)

        # Create output directories
        self.file_writer.create_directory(str(self.output_dir) or sdk_class_filename)

        # Generate models
        models_dir_name = str(self.models_dir).split("/")[-1]
        models_filename = "models"
        self._generate_models(
            models_dir=str(self.models_dir),
            models_filename=models_filename,
            file_ext=file_ext,
        )

        # Generate schema files
        self._generate_schema_files(models_filename=models_filename, file_ext=file_ext)

        # Generate src directory if needed
        src_dir = self.output_dir / "src"
        self._create_directory(str(src_dir))

        # Generate test directory if needed
        test_dir = self.output_dir / "tests"
        if self.generate_tests:
            self._create_directory(str(test_dir))

        # Generate handlers (tag/<operation_id>/<operation_id>.py)
        handler_file_paths_by_operation_id: Dict[str, str] = {}
        operation_metadata_by_tag: Dict[str, List[OperationMetadata]] = {}
        for op in self.metadata.operations:
            operation_id = op.operation_id
            tag_name = op.tag
            tag_dir, tag_class_name, tag_filename = self._get_tag_formats(tag_name)
            is_operation_without_tag = tag_name == ""
            tag_dir_path = src_dir / tag_dir
            handler_filename = operation_id
            handler_dir = handler_filename
            handler_file_dir_path = tag_dir_path / handler_dir
            self._create_directory(str(handler_file_dir_path))
            handler_file = handler_filename + file_ext
            handler_file_path = handler_file_dir_path / handler_file
            handler_class_name = Helpers.clean_capitalize(handler_filename)
            operation_metadata = OperationMetadata(
                handler_dir=handler_dir,
                handler_filename=handler_filename,
                handler_class_name=handler_class_name,
            )
            operation_handler_content = self._generate_handler_class(
                operation=op,
                parent_class_name=parent_class_name,
                parent_filename=sdk_class_filename,
                is_operation_without_tag=is_operation_without_tag,
                operation_metadata=operation_metadata,
                models_dir=models_dir_name,
                models_filename=models_filename,
            )
            handler_file_paths_by_operation_id[op.operation_id] = str(handler_file_path)
            self._write_and_format(str(handler_file_path), operation_handler_content)
            if tag_name not in operation_metadata_by_tag:
                operation_metadata_by_tag[tag_name] = []
            operation_metadata_by_tag[tag_name].append(operation_metadata)

            # TODO: not implemented
            # Generate tests
            if self.generate_tests:
                tag_test_dir_path = test_dir / tag_dir
                handler_test_file_dir_path = tag_test_dir_path / handler_filename
                self._create_directory(str(handler_test_file_dir_path))
                handler_test_file = handler_filename + "_test" + file_ext
                handler_test_file_path = handler_test_file_dir_path / handler_test_file
                test_content = ""
                # test_content = self._generate_tests(tag, operations)
                self._write_and_format(str(handler_test_file_path), test_content)

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
            self._create_directory(str(tag_dir_path))
            tag_file = tag_filename + file_ext
            tag_file_path = tag_dir_path / tag_file
            tag_class_content = self._generate_tag_class(
                parent_class_name=parent_class_name,
                sdk_class_filename=sdk_class_filename,
                tag_class_name=tag_class_name,
                tag_description=tag_description,
                operation_metadata=operation_metadata,
                models_dir=models_dir_name,
                models_filename=models_filename,
            )
            self._write_and_format(str(tag_file_path), tag_class_content)
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
                self._create_directory(str(tag_test_dir_path))

        # Generate base client
        operations_without_tags: List[
            OperationMetadata
        ] = operation_metadata_by_tag.get("", [])
        sdk_class_content = self._generate_sdk_class(
            parent_class_name=parent_class_name,
            tag_metadata=tag_metadata,
            operations_without_tags=operations_without_tags,
            models_dir=models_dir_name,
            models_filename=models_filename,
        )
        sdk_class_file = sdk_class_filename + file_ext
        sdk_class_file_path = src_dir / sdk_class_file
        self._write_and_format(str(sdk_class_file_path), sdk_class_content)

        Helpers.run_ruff_on_path(str(self.output_dir))

        # TODO: move to pyproject.toml for easy SDK PyPi packaging
        # Generate requirements.txt
        requirements_path = self.output_dir / "requirements.txt"
        requirements_content = self._generate_requirements()
        self.file_writer.write(str(requirements_path), requirements_content)

        # TODO: needs to be re-implemented
        # Generate README
        # readme_path = self.output_dir / "README.md"
        # readme_content = self._generate_readme(operations_by_tag)
        # self.file_writer.write(str(readme_path), readme_content)

        # TODO: ask costumers if they want openapi.json ALWAYS output OR ONLY if it is being generated
        # Load OpenAPI content
        openapi_file = self.output_dir / "openapi.json"
        content_loader = ContentLoader()
        openapi_content = content_loader.load_structured_data(
            self.metadata.openapi_input
        )
        # Add x-codeSamples to OpenAPI content
        if self.generate_x_code_samples:
            openapi_content = self._generate_x_code_samples(
                openapi_content=openapi_content,
                handler_file_paths_by_operation_id=handler_file_paths_by_operation_id,
                file_ext=file_ext,
            )
        # Write OpenAPI content to file
        self.file_writer.write(str(openapi_file), json.dumps(openapi_content, indent=2))
