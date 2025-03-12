#!/bin/bash

# Function to display help message
display_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -i, --input      Specify the OpenAPI spec URL"
    echo "  -n, --dry-run    Preview changes without making them"
    echo "  -g, --generate   Generate the client SDK only"
    echo "  -p, --push       Generate and push to a new branch"
    echo "  -h, --help       Display this help message"
    exit 1
}

# Parse command line arguments
DRY_RUN=false
GENERATE_ONLY=false
PUSH=false
SPEC_URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input)
            shift
            SPEC_URL=$1
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -g|--generate)
            GENERATE_ONLY=true
            shift
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -h|--help)
            display_help
            ;;
        *)
            echo "Unknown option: $1"
            display_help
            ;;
    esac
done

# Check if URL is provided
if [ -z "$SPEC_URL" ]; then
    echo "Error: OpenAPI spec URL is required. Use -i or --input to specify it."
    display_help
fi

# If no action flags are specified, display help
if [[ "$DRY_RUN" == "false" && "$GENERATE_ONLY" == "false" && "$PUSH" == "false" ]]; then
    display_help
fi

TEMP_FILE="/tmp/openapi_temp.json"

# Download the spec file
if [[ $SPEC_URL == *".yaml" ]] || [[ $SPEC_URL == *".yml" ]]; then
    # For YAML files, we need to convert to JSON
    curl -s "$SPEC_URL" | python -c "import sys, yaml, json; json.dump(yaml.safe_load(sys.stdin), sys.stdout)" > "$TEMP_FILE"
else
    # For JSON files, download directly
    curl -s "$SPEC_URL" > "$TEMP_FILE"
fi

# Extract the title and convert to lowercase with underscores
TITLE=$(cat "$TEMP_FILE" | python -c "import sys, json; print(json.load(sys.stdin).get('info', {}).get('title', '').lower().replace(' ', '_').replace('-', '_'))")

if [ -z "$TITLE" ]; then
    echo "Error: Could not extract title from OpenAPI spec"
    rm "$TEMP_FILE"
    exit 1
fi

# Append _client to the title
OUTPUT_DIR="${TITLE}_client"

# Create branch name
CURRENT_DATE=$(date +"%Y-%m-%d")
BRANCH_NAME=$(echo "${OUTPUT_DIR}" | tr '_' '-')-${CURRENT_DATE}

if [ "$DRY_RUN" = true ]; then
    echo "Dry run - would perform the following actions:"
    echo "- Create output directory: $OUTPUT_DIR"
    echo "- Create borea.config.json with:"
    echo "  - Input openapi files: ${OUTPUT_DIR}/openapi.json, ${SPEC_URL}"
    echo "  - Output clientSDK: ${OUTPUT_DIR}"
    if [ "$PUSH" = true ]; then
        echo "- Create and push branch: $BRANCH_NAME"
    fi
    rm "$TEMP_FILE"
    exit 0
fi

# Create borea.config.json
cat > borea.config.json << EOF
{
    "input": {
        "openapi": [
            "${OUTPUT_DIR}/openapi.json",
            "${SPEC_URL}"
        ]
    },
    "output": {
        "clientSDK": "${OUTPUT_DIR}"
    }
}
EOF

# Create output directory and copy spec file
mkdir -p "$OUTPUT_DIR"

# Clean up temp file
rm "$TEMP_FILE"

# Run the generator
python -m src.borea_python.cli generate

echo "Client generation completed. Output directory: $OUTPUT_DIR"

# Handle git operations if push is requested
if [ "$PUSH" = true ]; then
    # Create and switch to new branch
    git switch -c "$BRANCH_NAME"

    # Add and commit changes
    git add "$OUTPUT_DIR" borea.config.json -f
    git commit -m "feat: Generate client SDK for ${TITLE}"

    # Push branch upstream
    git push --set-upstream origin "$BRANCH_NAME"
    
    echo "Created and pushed branch: $BRANCH_NAME"
fi
