#!/usr/bin/env python3
"""
Startup script for the Blog Scraper FastAPI server
"""
import uvicorn
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Change to the project root so relative imports work
    os.chdir(project_root)
    
    # Add the project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Add the API module path
    api_module_path = "web-interface.src.app.api.scrape.main"
    
    print(f"Starting FastAPI server from: {os.getcwd()}")
    print(f"Loading module: {api_module_path}")
    
    # Run the FastAPI server
    uvicorn.run(
        f"{api_module_path}:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    ) 