from typing import Literal

from pydantic import BaseModel, Field


class XCodeSamples(BaseModel):
    """
    Model for XCodeSamples

    https://redocly.com/docs-legacy/api-reference-docs/specification-extensions/x-code-samples
    """

    lang: Literal[
        "C",
        "C#",
        "C++",
        "CoffeeScript",
        "CSS",
        "Dart",
        "DM",
        "Elixir",
        "Go",
        "Groovy",
        "HTML",
        "Java",
        "JavaScript",
        "Kotlin",
        "Objective-C",
        "Perl",
        "PHP",
        "PowerShell",
        "Python",
        "Ruby",
        "Rust",
        "Scala",
        "Shell",
        "Swift",
        "TypeScript",
    ] = Field(..., description="The language of the code sample")
    label: str = Field("", description="The label of the code sample")
    source: str = Field(..., description="The code sample source code")
