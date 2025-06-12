#!/bin/bash

# Install dependencies
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

# Run the Streamlit application
# The PORT environment variable is used by Streamlit to set the port.
# We also pass --server.port directly for robustness.
export STREAMLIT_SERVER_PORT=9000
streamlit run app.py --server.port 9000 --server.address 0.0.0.0
