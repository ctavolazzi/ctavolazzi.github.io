#!/bin/bash
#
# Version Release Script
# Usage: ./scripts/release.sh [patch|minor|major]
#
# Examples:
#   ./scripts/release.sh patch  # 0.1.0 → 0.1.1
#   ./scripts/release.sh minor  # 0.1.0 → 0.2.0
#   ./scripts/release.sh major  # 0.1.0 → 1.0.0
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
VERSION_FILE="$ROOT_DIR/VERSION"

# Check if VERSION file exists
if [ ! -f "$VERSION_FILE" ]; then
    echo -e "${RED}Error: VERSION file not found at $VERSION_FILE${NC}"
    exit 1
fi

# Read current version
CURRENT_VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Determine bump type
BUMP_TYPE=${1:-patch}

case $BUMP_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo -e "${RED}Error: Invalid bump type '$BUMP_TYPE'${NC}"
        echo "Usage: $0 [patch|minor|major]"
        exit 1
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

echo -e "${YELLOW}Bumping version: ${CURRENT_VERSION} → ${NEW_VERSION}${NC}"

# Update VERSION file
echo "$NEW_VERSION" > "$VERSION_FILE"

# Git operations
echo -e "${GREEN}Committing version bump...${NC}"
git add "$VERSION_FILE"
git commit -m "chore: bump version to ${NEW_VERSION}"

echo -e "${GREEN}Creating tag v${NEW_VERSION}...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

echo ""
echo -e "${GREEN}Version ${NEW_VERSION} is ready!${NC}"
echo ""
echo "To complete the release, run:"
echo -e "  ${YELLOW}git push origin main --tags${NC}"
echo ""
echo "This will trigger the GitHub Actions workflow to create a release."
