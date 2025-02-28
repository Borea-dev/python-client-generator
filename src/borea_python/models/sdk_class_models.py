from typing import List

from pydantic import BaseModel

from .openapi_models import HttpHeader


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

    class_name: str
    class_title: str
    class_description: str
    base_url: str
    http_headers: List[HttpHeader]
    tags: List[OpenAPITagMetadata]
