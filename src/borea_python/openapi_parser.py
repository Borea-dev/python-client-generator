import json
from typing import Any, Dict, List, Union

import click

from .content_loader import ContentLoader
from .models.openapi_models import (
    HttpHeader,
    HttpParameter,
    OpenAPIMetadata,
    Operation,
    SchemaMetadata,
)


class OpenAPIParser:
    """
    A parser to extract relevant API operation details from an OpenAPI specification.
    """

    def __init__(self, openapi_input: str, tag: str = "", operation_id: str = ""):
        """
        Initialize the parser by loading the OpenAPI specification.
        """
        content_loader = ContentLoader()
        self.openapi_spec = content_loader.load_structured_data(str(openapi_input))
        self.paths = self.openapi_spec.get("paths", {})
        self.components = self.openapi_spec.get("components", {}).get("schemas", {})
        self.tag = tag
        self.operation_id = operation_id
        self.openapi_input = openapi_input

    def parse(self) -> OpenAPIMetadata:
        """
        Parse the OpenAPI spec and return a list of operations filtered by criteria.
        """
        operations = []
        http_params = []
        for path, methods in self.paths.items():
            for method, details in methods.items():
                if "operationId" not in details:
                    continue
                if self.operation_id != "" and self.operation_id != details.get(
                    "operationId", ""
                ):
                    continue
                if self.tag != "" and self.tag not in details.get("tags", [""]):
                    continue
                operation = self._parse_operation(path, method, details)
                for http_param in operation.parameters:
                    self._add_unique_http_param(
                        http_params, http_param.model_dump(by_alias=True)
                    )
                operations.append(operation)
        headers = [
            HttpHeader(**http_param)
            for http_param in http_params
            if "header" in http_param["in"]
        ]
        openapi = self.openapi_spec.get("openapi", "")
        info = self.openapi_spec.get("info", {})
        servers = self.openapi_spec.get("servers", [])
        tags = self.openapi_spec.get("tags", [])
        components = self.openapi_spec.get("components", {})
        return OpenAPIMetadata(
            openapi_input=self.openapi_input,
            openapi=openapi,
            info=info,
            servers=servers,
            components=components,
            tags=tags,
            headers=headers,
            operations=operations,
        )

    def _add_unique_http_param(
        self, headers_list: List[Dict[str, Any]], new_header: Dict[str, Any]
    ) -> None:
        """Add a dictionary to the list only if 'name' and 'in' fields are unique."""
        if not any(
            h["name"] == new_header["name"] and h["in"] == new_header["in"]
            for h in headers_list
        ):
            headers_list.append(new_header)

    def _parse_operation(
        self, path: str, method: str, details: Dict[str, Any]
    ) -> Operation:
        """
        Extract relevant details for an API operation.
        """
        return Operation(
            tag=details.get("tags", [""])[0],
            operation_id=details["operationId"],
            method=method.upper(),
            path=path,
            summary=details.get("summary", ""),
            description=details.get("description", ""),
            parameters=self._parse_parameters(details.get("parameters", [])),
            request_body=self._parse_request_body(details.get("requestBody", {})),
        )

    def _parse_parameters(
        self, parameters: List[Dict[str, Any]]
    ) -> List[HttpParameter]:
        """
        Extract and format parameter details.
        """
        params = []
        for param in parameters:
            # "in" is a key word in Python so param_data had to be used
            param_data = {
                "name": param["name"],
                "in": param["in"],
                "required": param.get("required", False),
                "type": self._resolve_type(param.get("schema", {})),
                "description": param.get("description", ""),
                "original_name": param[
                    "name"
                ],  # Store the original name before cleaning
            }
            params.append(HttpParameter(**param_data))
        return params

    def _parse_request_body(
        self, request_body: Dict[str, Any]
    ) -> Union[SchemaMetadata, None]:
        """
        Extract and format request body details.
        """
        if not request_body:
            return None

        content = request_body.get("content", {})
        json_schema = content.get("application/json", {}).get("schema", {})
        return self._schema_metadata(json_schema)

    def _schema_metadata(self, schema: Dict[str, Any]) -> SchemaMetadata:
        """
        Extract relevant metadata from a given schema.
        """
        required = schema.get("required")
        nullable = schema.get("nullable")
        json_schema_type = self._resolve_type(schema)
        nested_json_schema_refs = self._extract_refs(schema)
        nested_json_schemas = self._resolve_nested_types(schema)

        return SchemaMetadata(
            required=required,
            nullable=nullable,
            type=json_schema_type,
            nested_json_schema_refs=nested_json_schema_refs,
            nested_json_schemas=nested_json_schemas,
            length_nested_json_schemas=len(nested_json_schemas),
        )

    def _resolve_type(self, schema: Dict[str, Any]) -> str:
        """
        Resolve and return the type of a given schema.
        """
        if "$ref" in schema:
            return schema["$ref"].split("/")[-1]
        if "allOf" in schema:
            return " & ".join([self._resolve_type(sub) for sub in schema["allOf"]])
        if "oneOf" in schema or "anyOf" in schema:
            return " | ".join(
                [
                    self._resolve_type(sub)
                    for sub in schema.get("oneOf", []) + schema.get("anyOf", [])
                ]
            )
        if "not" in schema:
            return f"Not[{self._resolve_type(schema['not'])}]"
        return schema.get("type", "any")

    def _extract_refs(self, schema: Dict[str, Any]) -> List[str]:
        """
        Recursively extract referenced schema names.
        """
        refs = []
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            refs.append(ref_name)
            if ref_name in self.components:
                refs.extend(self._extract_refs(self.components[ref_name]))
        for key in ["allOf", "oneOf", "anyOf", "not"]:
            if key in schema:
                for sub_schema in (
                    schema[key] if isinstance(schema[key], list) else [schema[key]]
                ):
                    refs.extend(self._extract_refs(sub_schema))
        return refs

    def _resolve_nested_types(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recursively resolve nested types within a schema, including all properties and nested properties.
        Handles $ref, allOf, oneOf, anyOf, not, and properties within objects and arrays.

        Args:
            schema: The OpenAPI schema to resolve

        Returns:
            List of resolved nested type schemas
        """
        nested_types = []
        if "type" in schema:
            self._traverse_dict(schema)
            nested_types.append(schema)
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            if ref_name in self.components:
                nested_types.extend(
                    self._resolve_nested_types(self.components[ref_name])
                )
        for key in ["allOf", "oneOf", "anyOf", "not"]:
            if key in schema:
                for sub_schema in (
                    schema[key] if isinstance(schema[key], list) else [schema[key]]
                ):
                    nested_types.extend(self._resolve_nested_types(sub_schema))
        return nested_types

    def _traverse_dict(
        self,
        d: Dict[str, Any],
        key: Union[str, int] = None,
        parent: Union[Dict[str, Any], List[Any]] = None,
    ):
        """
        Traverses a dictionary, resolving any '$ref' values.
        :param d: The dictionary to traverse.
        :param resolve_ref: A function that resolves '$ref' values.
        """
        for k, value in d.items():
            if k in ["$ref", "allOf", "oneOf", "anyOf", "not"]:
                schema_metadata = self._schema_metadata(d)
                parent[key] = schema_metadata
            elif isinstance(value, dict):
                self._traverse_dict(d=value, key=k, parent=d)
            elif isinstance(value, list):
                self._traverse_array(arr=value, key=k, parent=d)

    def _traverse_array(
        self,
        arr: List[Any],
        key: Union[str, int] = None,
        parent: Union[Dict[str, Any], List[Any]] = None,
    ):
        """
        Traverses an array (list), resolving any '$ref' values inside the array.
        :param arr: The array (list) to traverse.
        :param resolve_ref: A function that resolves '$ref' values.
        """
        for i, item in enumerate(arr):
            if isinstance(item, dict):
                self._traverse_dict(d=item, key=i, parent=arr)
            elif isinstance(item, list):
                self._traverse_array(arr=item, key=i, parent=arr)


@click.command()
@click.option(
    "--openapi-input",
    "-i",
    help="Path to OpenAPI specification file or URL",
    type=str,
)
@click.option(
    "--tag",
    default="",
    type=str,
)
@click.option(
    "--operation_id",
    default="",
    type=str,
)
def main(openapi_input: str, tag: str, operation_id: str):
    parser = OpenAPIParser(openapi_input, tag=tag, operation_id=operation_id)
    operations = parser.parse()
    click.echo(json.dumps(operations.model_dump(), indent=2))


if __name__ == "__main__":
    main()
