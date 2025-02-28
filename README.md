# Borea Python HTTP Client SDK Generator

Please learn more about Borea and our mission at [borea.dev](https://borea.dev) and our organization on GitHub [Borea-dev](https://github.com/Borea-dev).

This repository contains a Python HTTP client SDK generator. It generates a Python client from an OpenAPI specification.

## Setup

### Prerequisites

-   Python 3.8 or higher
-   pip (Python package installer)

### Quick Setup (Recommended)

Run the automated setup script:

_`source` is required to activate the virtual environment_

```bash
source ./setup.sh
```

Deactivate the Python venv:

```bash
deactivate
```

This script will:

1. Create a Python virtual environment (`.venv`)
2. Activate the virtual environment
3. Install all required dependencies

Available options:

```bash
setup.sh [OPTIONS]

Options:
  -r, --recreate    Recreate virtual environment (deletes existing .venv)
  -i, --reinstall   Reinstall all requirements
  -h, --help        Show this help message
```

### Manual Setup

If you prefer to set up manually, follow these steps:

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate the virtual environment:

-   On macOS/Linux:

```bash
source .venv/bin/activate
```

-   On Windows:

```bash
.venv\Scripts\activate
```

3. Install the package dependencies:

```bash
pip install -r src/requirements.txt
```

## Usage

### Running the Python SDK Generator

1. Ensure you have a valid OpenAPI specification file (`openapi.json`) in the root directory. Command line arguments and configuration are detailed below.

2. Run the SDK generator after configuration:

```bash
python -m src.borea_python.python_sdk_generator.python_sdk_generator
```

The generator will create the Python HTTP client SDK based on the OpenAPI specification.

### Configuration

**IMPORTANT!**

Command line arguments take precedence over settings in `borea.config.json`.

The project uses `borea.config.json` for configuration settings. Example config with the `defaults`:

```json
{
	"input": {
		"openapi": ["openapi.json"]
	},
	"output": {
		"clientSDK": "Formatted OpenAPI Title by default",
		"models": "models",
		"tests": false,
		"xCodeSamples": false
	},
	"ignores": []
}
```

-   `input`: map input options to array of values, ordered by precedence. For example, first value is a file path and the second is a URL. If the file cannot be found, then the URL will be used.
-   `output`: map output options to values
-   `ignore`: array of `glob` patterns to ignore. No file or directory matching the pattern will be created.

### Command line help

Show this help message with `--help`:

```bash
Usage: python -m src.borea_python.python_sdk_generator.python_sdk_generator
           [OPTIONS]

  Generate a Python SDK from an OpenAPI specification.

  The OpenAPI specification can be provided as a local file path or a URL. For
  URLs, both JSON and YAML formats are supported.

Options:
  -i, --openapi-input TEXT   Path to OpenAPI specification file or URL
  -o, --sdk-output TEXT      Output directory for the generated SDK
  -m, --models-output TEXT   Output directory for the generated models
  -t, --tests TEXT           Generate tests
  -x, --x-code-samples TEXT  Generate x-code-samples
  -c, --config TEXT          Path to borea.config.json
  --help                     Show this message and exit.
```

## Running Tests

**To be implemented...**

To run the test suite:

```bash
python -m pytest
```

## Project Structure

-   `src/` - Contains the source code for the SDK generator
-   `openapi.json` - OpenAPI specification file or wherever you decide to put it
-   `borea.config.json` - Configuration file for the generator
-   `.venv/` - Python virtual environment (created during setup)

## License

This project is licensed under the terms specified in the LICENSE file.
