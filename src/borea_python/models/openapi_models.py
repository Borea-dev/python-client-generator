# from __future__ import annotations  # Enables postponed evaluation of annotations
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class HttpParameter(BaseModel):
    """Represents an OpenAPI parameter"""

    name: str
    in_location: str = Field(..., alias="in")
    required: bool = False
    type: str
    description: str = ""
    original_name: str = ""  # Store the original parameter name before cleaning


class HttpHeader(HttpParameter):
    """Represents an OpenAPI header parameter"""

    in_location: Literal["header"] = "header"


class SchemaMetadata(BaseModel):
    """Represents an OpenAPI request body"""

    required: Optional[Union[bool, List[str]]] = None
    nullable: Optional[bool] = None
    type: str
    nested_json_schema_refs: List[str] = Field(default_factory=list)
    nested_json_schemas: List[Dict[str, Any]] = Field(default_factory=list)

    @property
    def length_nested_json_schemas(self) -> int:
        return len(self.nested_json_schemas)


class Operation(BaseModel):
    """Represents an OpenAPI operation"""

    tag: str
    operation_id: str
    method: str
    path: str
    summary: str = ""
    description: str = ""
    parameters: List[HttpParameter] = Field(default_factory=list)
    request_body: Optional[SchemaMetadata] = None


class Info(BaseModel):
    """Represents the 'info' object in OpenAPI metadata"""

    title: str
    version: str
    description: Optional[str] = ""
    termsOfService: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None
    license: Optional[Dict[str, Any]] = None


class Server(BaseModel):
    """Represents a server in OpenAPI metadata"""

    url: str
    description: Optional[str] = ""
    variables: Optional[Dict[str, Dict[str, Any]]] = None


class OpenAPITag(BaseModel):
    name: str
    description: str = ""


class Component(BaseModel):
    """Represents a component in OpenAPI metadata"""

    schemas: Dict[str, Any] = Field(default_factory=dict)
    securitySchemes: Dict[str, Any] = Field(default_factory=dict)


class OpenAPIMetadata(BaseModel):
    """Represents the parsed OpenAPI metadata"""

    openapi_input: str
    openapi: str
    info: Info
    servers: List[Server]
    components: Component
    tags: List[OpenAPITag]
    operations: List[Operation]
    headers: List[HttpHeader]
