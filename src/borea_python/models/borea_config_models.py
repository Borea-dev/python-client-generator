from typing import List, Optional

from pydantic import BaseModel, Field


class InputConfigJSON(BaseModel):
    """Configuration for input sources. JSON version."""

    openapi: List[str] = Field(default_factory=list)


class InputConfig(BaseModel):
    """Configuration for input sources. Parsed version"""

    openapi: Optional[str] = None


class OutputConfig(BaseModel):
    """Configuration for output locations."""

    clientSDK: Optional[str] = None
    models: Optional[str] = None
    tests: bool = False
    xCodeSamples: bool = False


class BoreaConfigJSON(BaseModel):
    """Configuration for the Borea SDK generator. JSON version."""

    input: InputConfigJSON = Field(default_factory=InputConfigJSON)
    output: OutputConfig = Field(default_factory=OutputConfig)
    ignores: List[str] = Field(default_factory=list)


class BoreaConfig(BaseModel):
    """Configuration for the Borea SDK generator."""

    input: InputConfig = Field(default_factory=InputConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    ignores: List[str] = Field(default_factory=list)
