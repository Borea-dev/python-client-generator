import json
from typing import Any, Callable, Dict, List, Set, Tuple, Union

import click

from .content_loader import ContentLoader
from .logger import Logger
from .models.openapi_models import (
    HttpHeader,
    HttpParameter,
    OpenAPIMetadata,
    OpenAPIOperation,
    OpenAPITag,
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
        self.parameters = self.openapi_spec.get("components", {}).get("parameters", {})
        self.schemas = self.openapi_spec.get("components", {}).get("schemas", {})
        self.tag = tag
        self.operation_id = operation_id
        self.openapi_input = openapi_input

        self.visited_refs = (
            set()
        )  # Track visited references to prevent infinite recursion
        self.json_schema_key_words = ["$ref"]  # , "allOf", "oneOf", "anyOf", "not"]
        self.openapi_schema_groupings = [
            "allOf",
            "oneOf",
            "anyOf",
            "not",
            "properties",
            "items",
        ]

    def parse(self) -> OpenAPIMetadata:
        """
        Parse the OpenAPI spec and return a list of operations filtered by criteria.
        """

        (
            operations,
            tags_from_paths,
            http_params,
        ) = self._get_operations_tags_http_params_from_paths()
        headers = [
            HttpHeader(**http_param)
            for http_param in http_params
            if "header" in http_param["in"]
        ]
        openapi: str = self.openapi_spec.get("openapi", "")
        info = self.openapi_spec.get("info", {})
        servers = self.openapi_spec.get("servers", [])
        tags = self._merge_path_and_spec_tags(tags_from_paths)
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

    def _get_operations_tags_http_params_from_paths(
        self,
    ) -> Tuple[List[OpenAPIOperation], List[str], List[HttpParameter]]:
        operations = []
        unique_operation_ids = set()
        tags = set()
        http_params = []
        for path, methods in self.paths.items():
            for method, details in methods.items():
                # if statements are for filtering parser for easier debugging
                if self.operation_id != "" and self.operation_id != details.get(
                    "operationId", ""
                ):
                    continue
                if self.tag != "" and self.tag not in details.get("tags", [""]):
                    continue

                operation: OpenAPIOperation = self._parse_operation(
                    path, method, details, unique_operation_ids
                )
                if operation.tag != "":
                    tags.add(operation.tag)
                for http_param in operation.parameters:
                    self._add_unique_http_param(
                        http_params, http_param.model_dump(by_alias=True)
                    )
                operations.append(operation)
        return operations, list(tags), http_params

    def _merge_path_and_spec_tags(self, tags_from_paths: List[str]) -> List[OpenAPITag]:
        """Merges tags found on the OpenAPI spec and tags found on each operation."""
        openapi_spec_tags: List[OpenAPITag] = self.openapi_spec.get("tags", [])
        spec_tag_names: List[OpenAPITag] = []
        for tag in openapi_spec_tags:
            if "name" not in tag:
                Logger.warn(f"Tag missing name: {tag}")
            else:
                spec_tag_names.append(tag.get("name", ""))
        for tag_name in tags_from_paths:
            if tag_name not in spec_tag_names:
                openapi_spec_tags.append(OpenAPITag(name=tag_name, description=""))
        return openapi_spec_tags

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
        self,
        path: str,
        method: str,
        details: Dict[str, Any],
        unique_operation_ids: Set[str],
    ) -> OpenAPIOperation:
        """
        Extract relevant details for an API operation.
        """
        # get first tag, ignore the rest
        tag = details.get("tags", [""])[0]
        operation_id = self._parse_operation_id(
            path, method, details, unique_operation_ids
        )
        method = method.upper()

        return OpenAPIOperation(
            tag=tag,
            operation_id=operation_id,
            method=method,
            path=path,
            summary=details.get("summary", ""),
            description=details.get("description", ""),
            parameters=self._parse_parameters(details.get("parameters", [])),
            request_body=self._parse_request_body(details.get("requestBody", {})),
        )

    def _parse_operation_id(
        self,
        path: str,
        method: str,
        details: Dict[str, Any],
        unique_operation_ids: Set[str],
    ) -> str:
        """
        Extract the operationId from the details.
        """
        # Handle case where no operationId exists
        operation_id = details.get("operationId", "")
        if not operation_id:
            Logger.warn(
                f"No operationId found for {path} {method}. Using: {method}_{path}"
            )
            operation_id = f"{method}_{path}"
        if operation_id in unique_operation_ids:
            Logger.warn(
                f"Duplicate operationId found: {operation_id}. Making unique by adding _duplicate"
            )
            operation_id = f"{operation_id}_duplicate"
        unique_operation_ids.add(operation_id)
        return operation_id

    def _resolve_param_ref(self, param: str) -> Dict[str, Any]:
        """
        Resolve a reference to a component in the OpenAPI spec.
        """
        schema_name = param["$ref"].split("/")[-1]
        return self.parameters.get(schema_name, {})

    def _parse_parameters(
        self, parameters: List[Dict[str, Any]]
    ) -> List[HttpParameter]:
        """
        Extract and format parameter details.
        """
        params = []
        for param in parameters:
            # TODO: if param if $ref: #component resolve param
            if "$ref" in param:
                param = self._resolve_param_ref(param)
            schema = param.get("schema", {})
            name = param["name"]
            in_ = param["in"]
            required = param.get("required", False)
            type_ = self._resolve_type(schema)
            nested_json_schema_refs = self._extract_refs(schema)
            type_is_schema = len(nested_json_schema_refs) > 0

            description = param.get("description", "")
            # "in" is a key word in Python so param_data had to be used
            param_data = {
                "name": name,
                "in": in_,
                "required": required,
                "type": type_,
                "type_is_schema": type_is_schema,
                "description": description,
                "original_name": name,  # Store the original name before cleaning
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

    def _schema_metadata(
        self, schema: Dict[str, Any], count: int = 0
    ) -> SchemaMetadata:
        """
        Extract relevant metadata from a given schema.
        """
        required = schema.get("required")
        nullable = schema.get("nullable")
        json_schema_type = self._resolve_type(schema)
        nested_json_schema_refs = self._extract_refs(schema)

        nested_json_schemas = self._resolve_nested_types(schema, count=count + 1)
        type_is_schema = len(nested_json_schema_refs) > 0

        return SchemaMetadata(
            required=required,
            nullable=nullable,
            type=json_schema_type,
            type_is_schema=type_is_schema,
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
            if ref_name in self.schemas:
                refs.extend(self._extract_refs(self.schemas[ref_name]))
            else:
                Logger.warn(f"Schema {ref_name} not found in schemas")

        self.loop_over_schema_groupings(schema, refs, self._extract_refs)

        return refs

    def _resolve_nested_types(
        self, schema: Dict[str, Any], count: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Recursively resolve nested types within a schema, including all properties and nested properties.
        Handles $ref, allOf, oneOf, anyOf, not, and properties within objects and arrays.

        Args:
            schema: The OpenAPI schema to resolve

        Returns:
            List of resolved nested type schemas
        """

        nested_types = []
        if not schema:  # Handle None or empty schema
            return nested_types

        if "type" in schema:
            self._traverse_dict(schema, count=count + 1)
            nested_types.append(schema)

        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            if ref_name in self.schemas:
                if ref_name not in self.visited_refs:
                    self.visited_refs.add(ref_name)  # Mark as visited

                    nested_types.extend(
                        self._resolve_nested_types(
                            self.schemas[ref_name], count=count + 1
                        )
                    )
                else:
                    # Logger.warn(f"Schema {ref_name} has already been visited")
                    pass
            else:
                Logger.warn(f"Schema {ref_name} not found in schemas")

        self.loop_over_schema_groupings(
            schema,
            nested_types,
            self._resolve_nested_types,
        )

        return nested_types

    def loop_over_schema_groupings(
        self,
        schema: Dict[str, Any],
        refs: List[str],
        schema_type_handler: Callable[[Dict[str, Any]], None],
    ):
        for key in self.openapi_schema_groupings:
            if key in schema:
                value_at_key = schema[key]
                if isinstance(value_at_key, list):
                    for sub_schema in value_at_key:
                        refs.extend(schema_type_handler(sub_schema))
                else:
                    refs.extend(schema_type_handler(value_at_key))

    def _traverse_dict(
        self,
        d: Dict[str, Any],
        parent_key: Union[str, int] = None,
        parent: Union[Dict[str, Any], List[Any]] = None,
        count: int = 0,
    ):
        """
        Traverses a dictionary, resolving any '$ref' values.
        :param d: The dictionary to traverse.
        :param resolve_ref: A function that resolves '$ref' values.
        """

        for d_key, value in d.items():
            if d_key in self.json_schema_key_words:
                self._update_parent_schema_with_schema_metadata(
                    d=d,
                    d_key=d_key,
                    parent_key=parent_key,
                    parent=parent,
                    count=count + 1,
                )

            elif isinstance(value, dict):
                self._traverse_dict(
                    d=value, parent_key=d_key, parent=d, count=count + 1
                )
            elif isinstance(value, list):
                self._traverse_array(
                    arr=value, parent_key=d_key, parent=d, count=count + 1
                )

    def _update_parent_schema_with_schema_metadata(
        self,
        d: Dict[str, Any],
        d_key: Union[str, int],
        parent_key: Union[str, int],
        parent: Dict[str, Any],
        count: int = 0,
    ):
        num_of_keys = len(d.keys())
        schema: Dict[str, Any] = {}
        schema_parent: Dict[str, Any] = parent

        # If the dictionary has more than one key, we need to create a new dictionary with ONLY the key
        if num_of_keys > 1:
            # schema_parent = d
            schema[d_key] = d[d_key]

        else:
            # schema_parent = parent
            schema = d

        schema_metadata = self._schema_metadata(schema, count=count + 1)

        schema_parent[parent_key] = schema_metadata

    def _traverse_array(
        self,
        arr: List[Any],
        parent_key: Union[str, int] = None,
        parent: Union[Dict[str, Any], List[Any]] = None,
        count: int = 0,
    ):
        """
        Traverses an array (list), resolving any '$ref' values inside the array.
        :param arr: The array (list) to traverse.
        :param resolve_ref: A function that resolves '$ref' values.
        """
        for i, item in enumerate(arr):
            if isinstance(item, dict):
                self._traverse_dict(d=item, parent_key=i, parent=arr, count=count + 1)
            elif isinstance(item, list):
                self._traverse_array(
                    arr=item, parent_key=i, parent=arr, count=count + 1
                )


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
