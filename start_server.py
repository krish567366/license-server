#!/usr/bin/env python3
"""
QuantumMeta License Server Startup Script
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlite3
        import smtplib
        logger.info("✅ All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("Installing server dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "-r", "requirements-server.txt"
            ], check=True)
            logger.info("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Failed to install dependencies")
            return False

def setup_environment():
    """Setup environment variables"""
    email_password = os.getenv("EMAIL_PASSWORD")
    
    if not email_password:
        logger.warning("⚠️  EMAIL_PASSWORD environment variable not set")
        logger.info("Email delivery will be simulated")
        logger.info("Set EMAIL_PASSWORD for real email delivery:")
        logger.info("export EMAIL_PASSWORD='your_app_password'")
    else:
        logger.info("✅ Email configuration found")
    
    # Ensure license directory exists
    license_dir = Path.home() / ".quantummeta"
    license_dir.mkdir(exist_ok=True)
    logger.info(f"✅ License directory: {license_dir}")

def generate_test_license():
    """Generate a test license for validation"""
    logger.info("🧪 Generating test license...")
    
    try:
        cmd = [
            "quantum-license", "generate",
            "-p", "quantum-test",
            "-u", "test@example.com", 
            "-f", "core,pro",
            "-m", "cab71040940caedf77d93edb4f1ef153",
            "-o", "valid_license.qkey"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info("✅ Test license generated successfully")
        logger.info(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to generate test license: {e}")
        return False

def start_server():
    """Start the FastAPI license server"""
    logger.info("🚀 Starting QuantumMeta License Server...")
    logger.info("📧 Admin email: bajpaikrishna715@gmail.com")
    
    try:
        import uvicorn
        uvicorn.run(
            "license_server:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")

def main():
    """Main startup function"""
    logger.info("🌟 QuantumMeta License Server - Starting Up")
    
    # Check current directory
    if not Path("license_server.py").exists():
        logger.error("❌ license_server.py not found in current directory")
        logger.info("Please run from the license directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Dependency check failed")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Generate test license
    generate_test_license()
    
    # Start server
    logger.info("🌐 Server will be available at: http://localhost:8000")
    logger.info("📊 Admin dashboard: http://localhost:8000/admin")
    logger.info("📋 API docs: http://localhost:8000/docs")
    
    start_server()

if __name__ == "__main__":
    main()
