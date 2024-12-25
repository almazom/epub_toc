#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Testing epub_toc package installation..."

# Activate existing venv
source "$PROJECT_ROOT/venv/bin/activate"

# Test installation
echo "Testing editable install..."
pip install -e "$PROJECT_ROOT"

# Verify installation
echo "Verifying installation..."
python -c "
import epub_toc
print(f'epub_toc version: {epub_toc.__version__}')
from epub_toc import EPUBTOCParser
print('Successfully imported EPUBTOCParser')
"

# Test importing all public interfaces
python -c "
from epub_toc import (
    EPUBTOCParser,
    TOCItem,
    EPUBTOCError
)
print('Successfully imported all public interfaces')
"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${RED}✗ Installation test failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}All installation tests completed successfully!${NC}" 