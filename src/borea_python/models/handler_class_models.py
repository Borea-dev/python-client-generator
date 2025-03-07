from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from .openapi_models import HttpParameter, SchemaMetadata


class MethodParameter(BaseModel):
    """Represents the data necessary to write method params, param types, and param docstrings"""

    required: Union[List[str], bool, None] = None
    name: str
    original_name: Optional[str] = None
    type: str
    description: str


class HandlerClassPyJinja(BaseModel):
    """Represent the data necessary to generate method"""

    models_dir: str
    models_filename: str
    parent_class_name: str
    parent_filename: str
    is_operation_without_tag: bool
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
