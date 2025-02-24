import json
import yaml
from pathlib import Path
from typing import Dict, Any, Union


class FileParser:
    """
    A utility class to handle importing JSON or YAML files and returning JSON data.
    """
    
    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a file containing either JSON or YAML data and return it as a JSON object.
        
        Args:
            file_path: Path to the file to parse (either JSON or YAML)
            
        Returns:
            Dict containing the parsed data
            
        Raises:
            ValueError: If the file extension is not supported or file cannot be parsed
            FileNotFoundError: If the file does not exist
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        suffix = file_path.suffix.lower()
        with open(file_path, 'r') as f:
            try:
                if suffix in ['.json']:
                    return json.load(f)
                elif suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported file extension: {suffix}. Must be .json, .yaml, or .yml")
            except (json.JSONDecodeError, yaml.YAMLError) as e:
                raise ValueError(f"Failed to parse {suffix} file: {str(e)}")
