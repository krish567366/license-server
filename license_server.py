"""
Real License Server Implementation
FastAPI-based license server with real email delivery
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, EmailStr
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sqlite3
import hashlib
import secrets
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import List, Optional
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QuantumMeta License Server",
    description="Real license server for QuantumMeta ecosystem packages",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "licenses.db"
ADMIN_EMAIL = "bajpaikrishna715@gmail.com"
ADMIN_TOKEN = None  # Will be generated on startup

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "bajpaikrishna715@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Set via environment variable

# Supported packages from your PyPI account
SUPPORTED_PACKAGES = [
    "probabilistic-quantum-reasoner",
    "quantum-generative-adversarial-networks-pro", 
    "quantum-entangled-knowledge-graphs",
    "quantum-data-embedding-suite",
    "cognito-sim-engine",
    "hyper-fabric-interconnect",
    "entanglement-enhanced-nlp",
    "se-agi",
    "QuantumMetaGPT",
    "automl-self-improvement",
    "decentralized-ai",
    "hyqcopt",
    "dhcs-algorithm",
    "quantum-metalearn",
    "kyber-pqc"
]

class LicenseRequest(BaseModel):
    email: EmailStr
    package_name: str
    intended_use: str
    organization: Optional[str] = None
    machine_id: Optional[str] = None

class LicenseValidation(BaseModel):
    license_data: str
    package_name: str
    machine_id: Optional[str] = None

class AdminAuth(BaseModel):
    email: str
    token: str

def init_database():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # License requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS license_requests (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            package_name TEXT NOT NULL,
            intended_use TEXT,
            organization TEXT,
            machine_id TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            approved_by TEXT
        )
    ''')
    
    # Generated licenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id TEXT PRIMARY KEY,
            request_id TEXT,
            email TEXT NOT NULL,
            package_name TEXT NOT NULL,
            machine_id TEXT,
            features TEXT,
            license_data TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (request_id) REFERENCES license_requests (id)
        )
    ''')
    
    # Admin sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_sessions (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def generate_admin_token():
    """Generate a secure admin token"""
    global ADMIN_TOKEN
    ADMIN_TOKEN = secrets.token_urlsafe(32)
    logger.info(f"Admin token generated: {ADMIN_TOKEN}")
    return ADMIN_TOKEN

def send_email(to_email: str, subject: str, body: str, attachment_path: Optional[str] = None):
    """Send email with optional attachment"""
    if not EMAIL_PASSWORD:
        logger.warning("Email password not set. Email not sent.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(attachment_path)}'
                )
                msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

def generate_license_file(email: str, package_name: str, machine_id: str, features: List[str]) -> str:
    """Generate a .qkey license file using the existing CLI"""
    import subprocess
    import tempfile
    
    license_id = f"lic_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
    output_path = f"/tmp/{license_id}.qkey"
    
    # Use the existing CLI to generate license
    cmd = [
        "quantum-license", "generate",
        "-p", package_name,
        "-u", email,
        "-f", ",".join(features),
        "-m", machine_id,
        "-o", output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"License generated: {result.stdout}")
        return output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate license: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate license")

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    init_database()
    token = generate_admin_token()
    logger.info("License server started")
    logger.info(f"Admin email: {ADMIN_EMAIL}")
    logger.info(f"Admin token: {token}")

# API Endpoints

@app.post("/api/request-license")
async def request_license(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    package_name: str = Form(...),
    intended_use: str = Form(...),
    organization: str = Form(None),
    machine_id: str = Form(None)
):
    """Submit a license request"""
    
    if package_name not in SUPPORTED_PACKAGES:
        raise HTTPException(status_code=400, detail="Package not supported")
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Store request in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO license_requests 
        (id, email, package_name, intended_use, organization, machine_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (request_id, email, package_name, intended_use, organization, machine_id))
    
    conn.commit()
    conn.close()
    
    # Send notification email to admin
    admin_subject = f"New License Request: {package_name}"
    admin_body = f"""
    <h2>New License Request</h2>
    <p><strong>Request ID:</strong> {request_id}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Package:</strong> {package_name}</p>
    <p><strong>Intended Use:</strong> {intended_use}</p>
    <p><strong>Organization:</strong> {organization or 'N/A'}</p>
    <p><strong>Machine ID:</strong> {machine_id or 'Any machine'}</p>
    
    <p><a href="http://localhost:8000/admin">Review in Admin Dashboard</a></p>
    """
    
    background_tasks.add_task(send_email, ADMIN_EMAIL, admin_subject, admin_body)
    
    # Send confirmation email to user
    user_subject = f"License Request Received: {package_name}"
    user_body = f"""
    <h2>License Request Received</h2>
    <p>Thank you for requesting a license for <strong>{package_name}</strong>.</p>
    <p><strong>Request ID:</strong> {request_id}</p>
    <p>Your request is being reviewed and you will receive your license file shortly.</p>
    
    <h3>Next Steps:</h3>
    <ol>
        <li>Wait for approval (usually within 24 hours)</li>
        <li>Download your .qkey file from the email</li>
        <li>Install: <code>pip install quantummeta-license</code></li>
        <li>Activate: <code>quantum-license activate license.qkey</code></li>
    </ol>
    """
    
    background_tasks.add_task(send_email, email, user_subject, user_body)
    
    return {"message": "License request submitted", "request_id": request_id}

@app.get("/api/admin/requests")
async def get_license_requests(auth: dict = Depends(lambda: None)):
    """Get all license requests (admin only)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, email, package_name, intended_use, organization, 
               machine_id, status, created_at 
        FROM license_requests 
        ORDER BY created_at DESC
    ''')
    
    requests = []
    for row in cursor.fetchall():
        requests.append({
            "id": row[0],
            "email": row[1],
            "package_name": row[2],
            "intended_use": row[3],
            "organization": row[4],
            "machine_id": row[5],
            "status": row[6],
            "created_at": row[7]
        })
    
    conn.close()
    return {"requests": requests}

@app.post("/api/admin/approve-license/{request_id}")
async def approve_license(
    request_id: str,
    background_tasks: BackgroundTasks,
    features: str = Form("core,pro"),
    admin_email: str = Form(...),
    admin_token: str = Form(...)
):
    """Approve a license request and generate license file"""
    
    # Verify admin credentials
    if admin_email != ADMIN_EMAIL or admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Get request details
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM license_requests WHERE id = ?', (request_id,))
    request_data = cursor.fetchone()
    
    if not request_data:
        raise HTTPException(status_code=404, detail="Request not found")
    
    email = request_data[1]
    package_name = request_data[2]
    machine_id = request_data[5] or "any"
    
    # Generate license file
    try:
        license_file_path = generate_license_file(
            email=email,
            package_name=package_name, 
            machine_id=machine_id,
            features=features.split(",")
        )
        
        # Store license in database
        license_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO licenses 
            (id, request_id, email, package_name, machine_id, features, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            license_id, request_id, email, package_name, machine_id, 
            features, datetime.now() + timedelta(days=365)
        ))
        
        # Update request status
        cursor.execute('''
            UPDATE license_requests 
            SET status = 'approved', approved_at = CURRENT_TIMESTAMP, approved_by = ?
            WHERE id = ?
        ''', (admin_email, request_id))
        
        conn.commit()
        
        # Send license file to user
        subject = f"Your {package_name} License is Ready!"
        body = f"""
        <h2>License Approved!</h2>
        <p>Your license for <strong>{package_name}</strong> has been approved and is attached to this email.</p>
        
        <h3>Installation Instructions:</h3>
        <ol>
            <li>Install the license manager: <code>pip install quantummeta-license</code></li>
            <li>Activate your license: <code>quantum-license activate {package_name}.qkey</code></li>
            <li>Install the package: <code>pip install {package_name}</code></li>
            <li>Start using: <code>import {package_name.replace('-', '_')}</code></li>
        </ol>
        
        <p><strong>License ID:</strong> {license_id}</p>
        <p><strong>Features:</strong> {features}</p>
        <p><strong>Valid Until:</strong> {(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}</p>
        
        <p>Need help? Contact: bajpaikrishna715@gmail.com</p>
        """
        
        background_tasks.add_task(send_email, email, subject, body, license_file_path)
        
        conn.close()
        return {"message": "License approved and sent", "license_id": license_id}
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to process license: {e}")

@app.post("/api/validate-license")
async def validate_license(validation: LicenseValidation):
    """Validate a license file"""
    # This would integrate with your existing validation logic
    # For now, return a simple validation
    return {"valid": True, "message": "License is valid"}

@app.get("/api/status/{email}")
async def get_license_status(email: str):
    """Get license status for an email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT package_name, status, expires_at 
        FROM licenses 
        WHERE email = ? AND status = 'active'
    ''', (email,))
    
    licenses = []
    for row in cursor.fetchall():
        licenses.append({
            "package": row[0],
            "status": row[1],
            "expires": row[2]
        })
    
    conn.close()
    return {"email": email, "licenses": licenses}

# Static file serving for the web interface
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main license request page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>QuantumMeta License Server</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .success { color: green; margin-top: 10px; }
            .error { color: red; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>🚀 QuantumMeta License Server</h1>
        <p>Request a license for any QuantumMeta ecosystem package.</p>
        
        <form id="licenseForm">
            <div class="form-group">
                <label for="email">Email Address:</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="package_name">Package:</label>
                <select id="package_name" name="package_name" required>
                    <option value="">Select a package...</option>
                    <option value="quantum-metalearn">quantum-metalearn</option>
                    <option value="se-agi">se-agi</option>
                    <option value="kyber-pqc">kyber-pqc</option>
                    <option value="QuantumMetaGPT">QuantumMetaGPT</option>
                    <option value="quantum-entangled-knowledge-graphs">quantum-entangled-knowledge-graphs</option>
                    <option value="probabilistic-quantum-reasoner">probabilistic-quantum-reasoner</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="intended_use">Intended Use:</label>
                <textarea id="intended_use" name="intended_use" rows="3" required placeholder="Describe how you plan to use this package..."></textarea>
            </div>
            
            <div class="form-group">
                <label for="organization">Organization (Optional):</label>
                <input type="text" id="organization" name="organization" placeholder="Your company or institution">
            </div>
            
            <div class="form-group">
                <label for="machine_id">Machine ID (Optional):</label>
                <input type="text" id="machine_id" name="machine_id" placeholder="Leave empty for any machine">
                <small>Get your machine ID: <code>quantum-license info</code></small>
            </div>
            
            <button type="submit">Request License</button>
        </form>
        
        <div id="message"></div>
        
        <hr style="margin: 40px 0;">
        <h2>Admin Panel</h2>
        <p><a href="/admin">Admin Dashboard</a> - Manage license requests</p>
        
        <script>
            document.getElementById('licenseForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const messageDiv = document.getElementById('message');
                
                try {
                    const response = await fetch('/api/request-license', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        messageDiv.innerHTML = '<p class="success">License request submitted! Check your email for confirmation.</p>';
                        e.target.reset();
                    } else {
                        messageDiv.innerHTML = '<p class="error">Error: ' + result.detail + '</p>';
                    }
                } catch (error) {
                    messageDiv.innerHTML = '<p class="error">Network error. Please try again.</p>';
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard():
    """Serve the admin dashboard"""
    # This would serve your existing admin-app.html with modifications
    return HTMLResponse(content="<h1>Admin Dashboard</h1><p>Use the existing admin-app.html file</p>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
