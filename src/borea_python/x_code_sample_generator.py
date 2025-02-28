from typing import Any, Dict

from .models.x_code_samples_models import XCodeSamples


class XCodeSampleGenerator:
    """Class to generate x-codeSamples for OpenAPI operations"""

    def __init__(
        self,
        openapi_content: Dict[str, Any],
        handler_file_paths_by_operation_id: Dict[str, str],
        file_ext: str,
    ):
        """
        Initialize CodeSampleGenerator

        Args:
            openapi_content: Dict containing OpenAPI content
            handler_file_paths_by_operation_id: Dict mapping operation IDs to file paths
            file_ext: Extension of generated files
        """
        self.file_ext = file_ext
        self.lang = "Python"
        self.openapi_content = openapi_content
        self.handler_file_paths_by_operation_id = handler_file_paths_by_operation_id

    def _create_code_sample(self, file_path: str, label: str) -> XCodeSamples:
        """
        Create an x-codeSamples object from a file

        Args:
            file_path: Path to the Python file
            label: Label for the code sample

        Returns:
            XCodeSamples object containing the file content
        """
        with open(file_path, "r") as f:
            content = f.read()

        # TODO: change label
        return XCodeSamples(lang=self.lang, label=label, source=content)

    def add_code_samples_from_file(
        self, operation: Dict[str, Any], file_path: str, label: str
    ) -> None:
        """
        Add x-codeSamples to an operation

        Args:
            operation: Operation to add the code sample to
            file_path: Path to the file
            label: Label for the code sample
        """
        code_sample = self._create_code_sample(file_path=file_path, label=label)
        operation["x-codeSamples"] = [code_sample.model_dump()]

    def add_code_samples(self) -> Dict[str, Any]:
        """
        Add x-codeSamples to each operation in the OpenAPI content

        Returns:
            Dict containing the modified OpenAPI content
        """
        # Iterate through paths and operations
        paths = self.openapi_content.get("paths", {})
        for path in paths.values():
            for operation in path.values():
                operation_id = operation.get("operationId")
                if (
                    operation_id
                    and operation_id in self.handler_file_paths_by_operation_id
                ):
                    file_path = self.handler_file_paths_by_operation_id[operation_id]
                    label = operation.get("description", "") or operation.get(
                        "summary", ""
                    )
                    self.add_code_samples_from_file(operation, file_path, label)

        return self.openapi_content
