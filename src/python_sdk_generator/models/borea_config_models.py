from pydantic import BaseModel, Field
from typing import List


class GeneratorConfig(BaseModel):
    """Configuration for the generator itself."""

    input: str = ""
    sdkOutput: str = ""
    modelsOutput: str = ""
    tests: bool = False


class BoreaConfig(BaseModel):
    """Configuration for the Borea SDK generator."""

    generator: GeneratorConfig = Field(default_factory=GeneratorConfig)
    ignores: List[str] = Field(default_factory=list)
