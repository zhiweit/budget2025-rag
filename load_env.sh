#!/bin/bash

# Script to handle direnv and load environment variables from .envrc

# Check if direnv is installed
if command -v direnv &> /dev/null; then
    echo "direnv is installed. Running direnv allow..."
    direnv allow
else
    echo "direnv is not installed. Loading environment variables manually..."
    
    # Source the .envrc file directly
    if [ -f .envrc ]; then
        echo "Loading variables from .envrc"
        set -a  # automatically export all variables
        source .envrc
        set +a
        echo "Environment variables loaded successfully!"
    else
        echo "Error: .envrc file not found!"
        exit 1
    fi
fi

# Print confirmation
echo "Environment is now ready. You can proceed with your commands." 