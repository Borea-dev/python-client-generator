from typing import List

from pydantic import BaseModel, Field

from .openapi_models import HttpHeader
from .tag_class_models import OperationMetadata


class OpenAPITagMetadata(BaseModel):
    """Represents the data necessary to import and append classes as properties"""

    tag: str
    tag_description: str
    tag_dir: str
    tag_filename: str
    tag_class_name: str
    tag_prop_name: str


class SdkClassPyJinja(BaseModel):
    """Represents the data the sdk_class.py.jinja template needs"""

    models_dir: str
    models_filename: str
    class_name: str
    class_title: str
    class_description: str
    base_url: str
    http_headers: List[HttpHeader] = Field(default_factory=list)
    tags: List[OpenAPITagMetadata] = Field(default_factory=list)
    operation_metadata: List[OperationMetadata] = Field(default_factory=list)
