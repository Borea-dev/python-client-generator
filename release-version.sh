#!/bin/bash

# Script to release a new version: updates pyproject.toml, creates git tag, and pushes to trigger release workflow
# Usage: ./release-version.sh [breaking|feature|fix] [--dry-run]
#        ./release-version.sh [-b|-feat|-fix] [-n]

set -e

# Initialize variables
DRY_RUN=false
RELEASE_TYPE=""

# Function to display usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] or $0 [TYPE] [--dry-run]"
    echo "Options:"
    echo "  -n, --dry-run     Dry run mode (no changes will be made)"
    echo "  -b, --breaking    Breaking change (major version increment)"
    echo "  -feat, --feature  Feature addition (minor version increment)"
    echo "  -fix, --fix       Bug fix (patch version increment)"
    exit 1
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    show_usage
fi

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -b|--breaking)
            if [ -n "$RELEASE_TYPE" ]; then
                echo "Error: Only one release type can be specified"
                show_usage
            fi
            RELEASE_TYPE="breaking"
            shift
            ;;
        -feat|--feature)
            if [ -n "$RELEASE_TYPE" ]; then
                echo "Error: Only one release type can be specified"
                show_usage
            fi
            RELEASE_TYPE="feature"
            shift
            ;;
        -fix|--fix)
            if [ -n "$RELEASE_TYPE" ]; then
                echo "Error: Only one release type can be specified"
                show_usage
            fi
            RELEASE_TYPE="fix"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Check if release type is specified
if [ -z "$RELEASE_TYPE" ]; then
    echo "Error: No release type specified"
    show_usage
fi

# Display dry run mode message if enabled
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE: No changes will be made"
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -E "^version = \"[0-9]+\.[0-9]+\.[0-9]+\"" pyproject.toml | sed -E 's/version = "([0-9]+\.[0-9]+\.[0-9]+)"/\1/')

if [ -z "$CURRENT_VERSION" ]; then
    echo "Error: Could not find version in pyproject.toml"
    exit 1
fi

echo "Current version: $CURRENT_VERSION"

# Split version into components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Update version according to release type
case $RELEASE_TYPE in
    breaking)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    feature)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    fix)
        PATCH=$((PATCH + 1))
        ;;
esac

# Create new version
NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
echo "New version: $NEW_VERSION"

# Perform actions based on dry run flag
if [ "$DRY_RUN" = true ]; then
    echo "Would update version in pyproject.toml from $CURRENT_VERSION to $NEW_VERSION"
    echo "Would commit changes with message: 'Release version $NEW_VERSION'"
    echo "Would create tag v$NEW_VERSION with message: 'Release version $NEW_VERSION'"
    echo "Would push to origin main with tags"
    echo "This would trigger your release workflow"
else
    # Update version in pyproject.toml
    sed -i '' "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
    echo "Updated version in pyproject.toml to $NEW_VERSION"

    # Commit the change
    git add pyproject.toml
    git commit -m "Release version $NEW_VERSION"
    echo "Committed changes"

    # Create and push tag
    git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
    git push origin main --tags
    echo "Created and pushed tag v$NEW_VERSION"

    echo "Version $NEW_VERSION released, changes committed, and tag pushed."
    echo "This should trigger your release workflow."
fi
