from typing import List

from pydantic import BaseModel


class OperationMetadata(BaseModel):
    handler_dir: str
    handler_filename: str
    handler_class_name: str


class TagClassPyJinja(BaseModel):
    """Represents the data the tag_class.py.jinja template needs"""

    models_dir: str
    models_filename: str
    parent_class_name: str
    parent_filename: str
    class_name: str
    description: str
    operation_metadata: List[OperationMetadata]
