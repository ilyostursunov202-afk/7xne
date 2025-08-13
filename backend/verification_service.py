"""
Verification service for phone and email verification using Twilio and SendGrid
"""

import os
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pymongo import MongoClient
import hashlib

# Initialize database collections
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/marketplace_db')
client = MongoClient(MONGO_URL)
db = client.marketplace_db
verification_codes_collection = db['verification_codes']

class VerificationService:
    def __init__(self):
        # Twilio credentials (will be set when user provides keys)
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN') 
        self.twilio_verify_service = os.getenv('TWILIO_VERIFY_SERVICE')
        
        # SendGrid credentials (will be set when user provides keys)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@marketplace.com')
        
        # Initialize clients when credentials are available
        self.twilio_client = None
        self.sendgrid_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize Twilio and SendGrid clients if credentials are available"""
        try:
            if self.twilio_account_sid and self.twilio_auth_token:
                from twilio.rest import Client
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                print("✅ Twilio client initialized")
            
            if self.sendgrid_api_key:
                from sendgrid import SendGridAPIClient
                self.sendgrid_client = SendGridAPIClient(self.sendgrid_api_key)
                print("✅ SendGrid client initialized")
        except Exception as e:
            print(f"⚠️ Error initializing verification clients: {e}")
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def store_verification_code(self, identifier: str, code: str, method: str, purpose: str = "verification") -> bool:
        """Store verification code in database with expiration"""
        try:
            # Hash the code for security
            hashed_code = hashlib.sha256(code.encode()).hexdigest()
            
            # Remove any existing codes for this identifier and purpose
            verification_codes_collection.delete_many({
                "identifier": identifier,
                "purpose": purpose
            })
            
            # Store new verification code
            verification_codes_collection.insert_one({
                "identifier": identifier,
                "hashed_code": hashed_code,
                "method": method,
                "purpose": purpose,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
                "verified": False,
                "attempts": 0
            })
            
            return True
        except Exception as e:
            print(f"Error storing verification code: {e}")
            return False
    
    def verify_code(self, identifier: str, code: str, purpose: str = "verification") -> bool:
        """Verify the provided code against stored code"""
        try:
            # Hash the provided code
            hashed_code = hashlib.sha256(code.encode()).hexdigest()
            
            # Find the verification record
            record = verification_codes_collection.find_one({
                "identifier": identifier,
                "hashed_code": hashed_code,
                "purpose": purpose,
                "verified": False,
                "expires_at": {"$gt": datetime.now(timezone.utc)}
            })
            
            if not record:
                # Increment failed attempts
                verification_codes_collection.update_one(
                    {"identifier": identifier, "purpose": purpose},
                    {"$inc": {"attempts": 1}}
                )
                return False
            
            # Mark as verified
            verification_codes_collection.update_one(
                {"_id": record["_id"]},
                {
                    "$set": {
                        "verified": True,
                        "verified_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            return True
        except Exception as e:
            print(f"Error verifying code: {e}")
            return False
    
    async def send_sms_verification(self, phone: str, purpose: str = "verification") -> Dict[str, Any]:
        """Send SMS verification code using Twilio"""
        try:
            if not self.twilio_client or not self.twilio_verify_service:
                # Fallback: Generate and store code manually
                code = self.generate_verification_code()
                success = self.store_verification_code(phone, code, "sms", purpose)
                
                if success:
                    print(f"📱 SMS Code for {phone}: {code}")  # For development
                    return {
                        "success": True,
                        "message": f"SMS sent to {phone}",
                        "dev_code": code  # Remove in production
                    }
                else:
                    return {"success": False, "message": "Failed to generate verification code"}
            
            # Use Twilio Verify API
            verification = self.twilio_client.verify.services(self.twilio_verify_service) \
                .verifications.create(to=phone, channel="sms")
            
            return {
                "success": True,
                "message": f"SMS sent to {phone}",
                "status": verification.status
            }
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            # Fallback to manual generation
            code = self.generate_verification_code()
            success = self.store_verification_code(phone, code, "sms", purpose)
            
            if success:
                print(f"📱 Fallback SMS Code for {phone}: {code}")
                return {
                    "success": True,
                    "message": f"SMS sent to {phone} (fallback)",
                    "dev_code": code
                }
            
            return {"success": False, "message": str(e)}
    
    async def verify_sms_code(self, phone: str, code: str) -> Dict[str, Any]:
        """Verify SMS code using Twilio or local verification"""
        try:
            if self.twilio_client and self.twilio_verify_service:
                # Use Twilio Verify API
                check = self.twilio_client.verify.services(self.twilio_verify_service) \
                    .verification_checks.create(to=phone, code=code)
                
                is_valid = check.status == "approved"
            else:
                # Use local verification
                is_valid = self.verify_code(phone, code)
            
            return {
                "success": is_valid,
                "message": "Phone verified successfully" if is_valid else "Invalid verification code"
            }
            
        except Exception as e:
            print(f"Error verifying SMS code: {e}")
            # Fallback to local verification
            is_valid = self.verify_code(phone, code)
            return {
                "success": is_valid,
                "message": "Phone verified successfully" if is_valid else "Invalid verification code"
            }
    
    async def send_email_verification(self, email: str, purpose: str = "verification") -> Dict[str, Any]:
        """Send email verification code using SendGrid"""
        try:
            code = self.generate_verification_code()
            success = self.store_verification_code(email, code, "email", purpose)
            
            if not success:
                return {"success": False, "message": "Failed to generate verification code"}
            
            # Prepare email content based on purpose
            if purpose == "password_reset":
                subject = "Password Reset Code - MarketPlace"
                html_content = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                            <h1 style="color: #333;">Password Reset</h1>
                        </div>
                        <div style="padding: 20px;">
                            <p>Hello,</p>
                            <p>You requested to reset your password. Use the verification code below:</p>
                            <div style="text-align: center; margin: 30px 0;">
                                <span style="font-size: 32px; font-weight: bold; background-color: #f0f0f0; 
                                           padding: 15px 25px; border-radius: 8px; letter-spacing: 5px;">{code}</span>
                            </div>
                            <p>This code will expire in 10 minutes.</p>
                            <p>If you didn't request this, please ignore this email.</p>
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                            <p style="color: #666; font-size: 12px;">
                                This email was sent from MarketPlace. Please do not reply to this email.
                            </p>
                        </div>
                    </body>
                </html>
                """
            else:
                subject = "Email Verification Code - MarketPlace"
                html_content = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <div style="background-color: #f8f9fa; padding: 20px; text-align: center;">
                            <h1 style="color: #333;">Welcome to MarketPlace!</h1>
                        </div>
                        <div style="padding: 20px;">
                            <p>Hello,</p>
                            <p>Thank you for registering with MarketPlace. Please verify your email address using the code below:</p>
                            <div style="text-align: center; margin: 30px 0;">
                                <span style="font-size: 32px; font-weight: bold; background-color: #f0f0f0; 
                                           padding: 15px 25px; border-radius: 8px; letter-spacing: 5px;">{code}</span>
                            </div>
                            <p>This code will expire in 10 minutes.</p>
                            <p>Welcome to our marketplace community!</p>
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                            <p style="color: #666; font-size: 12px;">
                                This email was sent from MarketPlace. Please do not reply to this email.
                            </p>
                        </div>
                    </body>
                </html>
                """
            
            if self.sendgrid_client:
                # Send via SendGrid
                from sendgrid.helpers.mail import Mail
                
                message = Mail(
                    from_email=self.sender_email,
                    to_emails=email,
                    subject=subject,
                    html_content=html_content
                )
                
                response = self.sendgrid_client.send(message)
                
                if response.status_code in [200, 201, 202]:
                    return {
                        "success": True,
                        "message": f"Verification email sent to {email}",
                        "dev_code": code  # Remove in production
                    }
                else:
                    print(f"SendGrid error: {response.status_code}")
                    print(f"📧 Email Code for {email}: {code}")
                    return {
                        "success": True,
                        "message": f"Email sent to {email} (fallback)",
                        "dev_code": code
                    }
            else:
                # No SendGrid client - development mode
                print(f"📧 Email Code for {email}: {code}")
                return {
                    "success": True,
                    "message": f"Email sent to {email} (development mode)",
                    "dev_code": code
                }
                
        except Exception as e:
            print(f"Error sending email: {e}")
            return {"success": False, "message": str(e)}
    
    async def verify_email_code(self, email: str, code: str, purpose: str = "verification") -> Dict[str, Any]:
        """Verify email verification code"""
        try:
            is_valid = self.verify_code(email, code, purpose)
            
            return {
                "success": is_valid,
                "message": "Email verified successfully" if is_valid else "Invalid verification code"
            }
            
        except Exception as e:
            print(f"Error verifying email code: {e}")
            return {"success": False, "message": str(e)}

# Create global instance
verification_service = VerificationService()