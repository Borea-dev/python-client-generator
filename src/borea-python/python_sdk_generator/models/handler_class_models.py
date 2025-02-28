from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from ...openapi_parser.models import HttpParameter, SchemaMetadata


class MethodParameter(BaseModel):
    """Represents the data necessary to write method params, param types, and param docstrings"""

    required: Union[List[str], bool, None] = None
    name: str
    original_name: Optional[str] = None
    type: str
    description: str


class HandlerClassPyJinja(BaseModel):
    """Represent the data necessary to generate method"""

    parent_class_name: str
    parent_filename: str
    class_name: str
    method_name: str
    description: str
    required_method_params: List[MethodParameter]
    optional_method_params: List[MethodParameter]
    http_method: Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    path: str
    http_params: List[HttpParameter] = Field(default_factory=[])
    request_body: Optional[SchemaMetadata] = None
    nested_schema: Optional[Dict[str, Any]] = None
