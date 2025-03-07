# Borea Python HTTP Client SDK Generator

Please learn more about Borea and our mission at [borea.dev](https://borea.dev) and our organization on GitHub [Borea-dev](https://github.com/Borea-dev).

This repository contains a Python HTTP client SDK generator. It generates a Python client from an OpenAPI specification.

## Table of Contents

-   [Getting Started](#getting-started)
-   [Installation](#installation)
-   [Usage](#usage)
-   [Running Tests](#running-tests)
-   [Project Structure](#project-structure)
-   [Manual Install](#manual-install)
-   [License](#license)

## Getting Started <a id="getting-started"></a>

### Prerequisites

-   Python 3.8 or higher
-   pip (Python package installer)

### Installation <a id="installation"></a>

Available as [borea-python](https://pypi.org/project/borea-python/) on PyPI.

```bash
pip install borea-python
```

For info on cloning and installing manually read [**Manual Install**](#manual-install).

## Usage <a id="usage"></a>

### Running the Python SDK Generator

The SDK generator provides two main commands:

1. `init` - Creates a new `borea.config.json` configuration file
2. `generate` - Generates a Python SDK from an OpenAPI specification

If no command is specified, the help message will be displayed.

#### Initialize a new configuration file

```bash
python -m borea_python.cli init
```

This will create a new `borea.config.json` file in the current directory with default settings. If the file already exists, you will be prompted to confirm overwriting it.

#### Generate the SDK

```bash
python -m borea_python.cli generate [OPTIONS]
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

```bash
python -m borea_python.cli generate --help
```

Output:

```
Usage: python -m borea_python.cli generate [OPTIONS]

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

## Running Tests <a id="running-tests"></a>

**To be implemented...**

To run the test suite:

```bash
python -m pytest
```

## Project Structure <a id="project-structure"></a>

-   `src/` - Contains the source code for the SDK generator
-   `openapi.json` - OpenAPI specification file or wherever you decide to put it
-   `borea.config.json` - Configuration file for the generator
-   `.venv/` - Python virtual environment (created during setup)

## Manual Install <a id="manual-install"></a>

### Clone repo

```bash
git clone https://github.com/Borea-dev/python-client-generator.git
```

Run the automated setup script:

_`source` is required to activate the virtual environment_

```bash
source ./setup-venv.sh
```

This script will:

1. Create a Python virtual environment (`.venv`)
2. Activate the virtual environment
3. Install all required dependencies

Available options:

```bash
setup-venv.sh [OPTIONS]

Options:
  -r, --recreate    Recreate virtual environment (deletes existing .venv)
  -i, --reinstall   Reinstall all requirements
  -h, --help        Show this help message
```

## License <a id="license"></a>

This project is licensed under the terms specified in the LICENSE file.
