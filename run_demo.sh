#!/bin/bash
# Launch the AM Printability Screening Web App

echo "========================================"
echo "AM Printability Screening System"
echo "Starting Web Interface..."
echo "========================================"
echo ""

# Check if streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install streamlit plotly trimesh numpy scipy rtree --break-system-packages -q
fi

echo "Starting server..."
echo ""
echo "👉 The app will open in your browser at: http://localhost:8501"
echo "👉 Press Ctrl+C to stop the server"
echo ""

# Launch streamlit
streamlit run app_printability_demo.py --server.port 8501 --server.headless false
