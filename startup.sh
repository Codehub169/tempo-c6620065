#!/bin/bash
set -e

# Ensure script is run from its own directory or that paths are adjusted accordingly if not
# cd "$(dirname "$0")" # Optional: if requirements.txt or app.py are not in PWD

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f requirements.txt ]; then
  echo "Found requirements.txt, installing dependencies..."
  pip install -r requirements.txt
else
  echo "requirements.txt not found, skipping dependency installation."
fi

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "Streamlit could not be found. Please ensure it is installed and in your PATH."
    exit 1
fi

# Run the Streamlit application
# The PORT environment variable is used by Streamlit to set the port.
# We also pass --server.port directly for robustness.
# Default to port 9000 if PORT is not set.
APP_PORT=${PORT:-9000}

echo "Starting Streamlit application on port ${APP_PORT}..."
streamlit run app.py --server.port ${APP_PORT} --server.address 0.0.0.0
