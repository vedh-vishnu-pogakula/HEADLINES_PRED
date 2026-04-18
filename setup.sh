#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Headline Oracle Setup & Runner ===${NC}"
echo -e "${YELLOW}Mitigating the PyTorch + Python 3.13 macOS deadlock...${NC}\n"

# 1. Check for Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo -e "${RED}Error: Python 3.12 could not be found.${NC}"
    echo "To fix the PyTorch deadlock on macOS, this app requires Python 3.12."
    echo ""
    echo "Please install Python 3.12 and try again."
    echo "Example using Homebrew: brew install python@3.12"
    exit 1
fi

echo -e "✓ Found Python 3.12 at: $(which python3.12)"

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "\n⏳ Creating Python 3.12 virtual environment in .venv..."
    python3.12 -m venv .venv
    echo -e "✓ Virtual environment created."
else
    echo -e "✓ Virtual environment .venv already exists."
fi

# 3. Activate and Install dependencies
echo -e "\n⏳ Activating virtual environment and ensuring dependencies are installed..."
source .venv/bin/activate

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo -e "✓ Environment is ready!"

# 4. Start the Application
echo -e "\n${GREEN}✦ Starting Gradio App ✦${NC}"
exec python app.py
