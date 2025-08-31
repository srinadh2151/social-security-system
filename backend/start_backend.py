#!/usr/bin/env python3
"""
Backend Startup Script

Starts the Social Security Application Backend with proper configuration.
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def main():
    """Start the backend server."""
    print("🚀 Starting Social Security Application Backend...")
    print("=" * 60)
    
    # Configuration
    config = {
        "app": "backend.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "log_level": "info",
        "access_log": True
    }
    
    print(f"📡 Server will start on: http://{config['host']}:{config['port']}")
    print(f"📚 API Documentation: http://{config['host']}:{config['port']}/docs")
    print(f"🔄 Auto-reload: {config['reload']}")
    print("=" * 60)
    
    # Start server
    uvicorn.run(**config)

if __name__ == "__main__":
    main()