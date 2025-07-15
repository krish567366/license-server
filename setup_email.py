#!/usr/bin/env python3
"""
Email Setup for QuantumMeta License Server
"""

import os
import sys
import getpass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_connection(email, password):
    """Test Gmail SMTP connection"""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def send_test_email(email, password):
    """Send a test email"""
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = email
        msg['Subject'] = "QuantumMeta License Server - Test Email"
        
        body = """
        <h2>🚀 QuantumMeta License Server</h2>
        <p>This is a test email from your license server!</p>
        <p>Email delivery is working correctly.</p>
        <p><strong>Server Status:</strong> ✅ Ready</p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(email, email, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def main():
    """Main setup function"""
    print("🌟 QuantumMeta License Server - Email Setup")
    print("=" * 50)
    
    email = "bajpaikrishna715@gmail.com"
    print(f"📧 Admin Email: {email}")
    
    print("\n📋 Gmail App Password Setup Instructions:")
    print("1. Go to Google Account settings")
    print("2. Enable 2-Factor Authentication")
    print("3. Generate an App Password for 'Mail'")
    print("4. Use that app password (not your regular password)")
    print("5. Guide: https://support.google.com/accounts/answer/185833")
    
    print(f"\n🔑 Enter Gmail App Password for {email}:")
    password = getpass.getpass("App Password: ")
    
    if not password:
        print("❌ No password provided")
        sys.exit(1)
    
    print("\n🧪 Testing email connection...")
    if test_email_connection(email, password):
        print("✅ Email connection successful!")
        
        print("\n📨 Sending test email...")
        if send_test_email(email, password):
            print("✅ Email setup complete!")
            
            # Set environment variable for current session
            os.environ["EMAIL_PASSWORD"] = password
            
            # Create .env file
            with open(".env", "w") as f:
                f.write(f"EMAIL_PASSWORD={password}\n")
            
            print("\n💾 Environment variable saved to .env file")
            print("🚀 You can now start the license server:")
            print("   python start_server.py")
            
        else:
            print("❌ Test email failed")
            sys.exit(1)
    else:
        print("❌ Email connection failed")
        print("Please check your app password and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()
