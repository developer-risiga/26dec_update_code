import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, config_file="config/notifications_config.json"):
        """
        Initialize notification system for Butler Assistant
        """
        self.config = self.load_config(config_file)
        
    def load_config(self, config_file):
        """Load email and SMS configuration"""
        default_config = {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "your_email@gmail.com",
                "sender_password": "your_app_password",  # Use App Password, not regular password
                "admin_email": "admin@example.com"
            },
            "sms": {
                "provider": "twilio",  # or "textlocal" for India
                "account_sid": "your_twilio_account_sid",
                "auth_token": "your_twilio_auth_token",
                "from_number": "+1234567890",
                "textlocal_api_key": "your_textlocal_key",  # For Indian numbers
                "textlocal_sender": "BUTLER"
            },
            "test_mode": True  # Set to False in production
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"✅ Loaded notification config from {config_file}")
                return config
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file {config_file} not found. Using defaults.")
            # Create config directory and file
            import os
            os.makedirs("config", exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
                logger.info(f"📁 Created default config at {config_file}")
            return default_config
    
    def send_email(self, recipient_email, subject, body, is_html=False):
        """
        Send email notification
        """
        if self.config['test_mode']:
            logger.info(f"📧 [TEST MODE] Would send email to {recipient_email}: {subject}")
            print(f"\n📧 [TEST] Email to {recipient_email}:")
            print(f"Subject: {subject}")
            print(f"Body: {body[:100]}...")
            return True
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['sender_email']
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.config['email']['smtp_server'], 
                                 self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['sender_email'],
                        self.config['email']['sender_password'])
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.config['email']['sender_email'], 
                          recipient_email, text)
            server.quit()
            
            logger.info(f"✅ Email sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {recipient_email}: {e}")
            return False
    
    def send_sms(self, phone_number, message):
        """
        Send SMS notification
        Supports Twilio (International) and TextLocal (India)
        """
        if self.config['test_mode']:
            logger.info(f"📱 [TEST MODE] Would send SMS to {phone_number}: {message[:50]}...")
            print(f"\n📱 [TEST] SMS to {phone_number}:")
            print(f"Message: {message[:100]}...")
            return True
            
        try:
            provider = self.config['sms'].get('provider', 'twilio')
            
            if provider == 'twilio':
                # Using Twilio
                from twilio.rest import Client
                client = Client(self.config['sms']['account_sid'],
                              self.config['sms']['auth_token'])
                
                message = client.messages.create(
                    body=message,
                    from_=self.config['sms']['from_number'],
                    to=phone_number
                )
                logger.info(f"✅ SMS sent via Twilio to {phone_number}")
                return True
                
            elif provider == 'textlocal':
                # Using TextLocal (for India)
                url = "https://api.textlocal.in/send/"
                params = {
                    'apikey': self.config['sms']['textlocal_api_key'],
                    'numbers': phone_number,
                    'message': message,
                    'sender': self.config['sms'].get('textlocal_sender', 'BUTLER')
                }
                
                response = requests.post(url, data=params)
                result = response.json()
                
                if result['status'] == 'success':
                    logger.info(f"✅ SMS sent via TextLocal to {phone_number}")
                    return True
                else:
                    logger.error(f"❌ TextLocal error: {result.get('errors', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to send SMS to {phone_number}: {e}")
            return False
    
    def notify_booking_confirmation(self, service_type, user_details, vendor_details):
        """
        Send notifications for booking confirmation
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        booking_id = f"BLR{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Email content
        email_subject = f"✅ Booking Confirmed: {service_type} - {booking_id}"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2 style="color: #4CAF50;">🎉 Booking Confirmed!</h2>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Booking Details:</h3>
                <p><strong>Booking ID:</strong> {booking_id}</p>
                <p><strong>Service:</strong> {service_type}</p>
                <p><strong>Booking Time:</strong> {timestamp}</p>
                <p><strong>Status:</strong> Confirmed ✅</p>
            </div>
            
            <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>User Information:</h3>
                <p><strong>Name:</strong> {user_details.get('name', 'Not provided')}</p>
                <p><strong>Contact:</strong> {user_details.get('phone', 'Not provided')}</p>
                <p><strong>Email:</strong> {user_details.get('email', 'Not provided')}</p>
                <p><strong>Address:</strong> {user_details.get('address', 'Not provided')}</p>
            </div>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Vendor Information:</h3>
                <p><strong>Service Provider:</strong> {vendor_details.get('name', 'Local Professional')}</p>
                <p><strong>Contact:</strong> {vendor_details.get('phone', 'Will contact shortly')}</p>
                <p><strong>ETA:</strong> Within 2 hours</p>
            </div>
            
            <hr>
            <p style="color: #666; font-size: 12px;">
                This is an automated message from Butler Assistant.
                <br>For support, contact: support@butler-assistant.com
            </p>
        </body>
        </html>
        """
        
        # SMS content
        sms_message = f"Butler: {service_type} booking confirmed. ID: {booking_id}. Professional will arrive within 2 hours. Contact: {vendor_details.get('phone', 'provided shortly')}"
        
        results = {
            'user_email': False,
            'user_sms': False,
            'vendor_email': False,
            'vendor_sms': False,
            'booking_id': booking_id
        }
        
        # Send to USER
        if user_details.get('email'):
            results['user_email'] = self.send_email(
                user_details['email'],
                email_subject,
                email_body,
                is_html=True
            )
        
        if user_details.get('phone'):
            results['user_sms'] = self.send_sms(
                user_details['phone'],
                sms_message
            )
        
        # Send to VENDOR
        if vendor_details.get('email'):
            vendor_email_body = f"""
            New {service_type} booking! 
            Booking ID: {booking_id}
            Customer: {user_details.get('name', 'Unknown')}
            Phone: {user_details.get('phone', 'N/A')}
            Address: {user_details.get('address', 'N/A')}
            Time: {timestamp}
            Please contact customer within 30 minutes.
            """
            
            results['vendor_email'] = self.send_email(
                vendor_details['email'],
                f"New Booking: {service_type} - {booking_id}",
                vendor_email_body
            )
        
        if vendor_details.get('phone'):
            vendor_sms = f"New {service_type} booking: {user_details.get('name')} - {user_details.get('phone', 'N/A')}. Address: {user_details.get('address', 'Check email')}. Booking ID: {booking_id}"
            results['vendor_sms'] = self.send_sms(
                vendor_details['phone'],
                vendor_sms
            )
        
        return results


# Singleton instance
notification_manager = NotificationManager()

if __name__ == "__main__":
    # Test the notification system
    print("🧪 Testing notification system...")
    
    test_user = {
        "name": "John Doe",
        "email": "test@example.com",
        "phone": "+919876543210",
        "address": "123 Main St, City"
    }
    
    test_vendor = {
        "name": "City Electricians",
        "email": "vendor@example.com",
        "phone": "+919876543211"
    }
    
    nm = NotificationManager()
    results = nm.notify_booking_confirmation(
        "electrician",
        test_user,
        test_vendor
    )
    
    print(f"\n📊 Notification Results:")
    print(f"Booking ID: {results['booking_id']}")
    print(f"User Email: {'✅' if results['user_email'] else '❌'}")
    print(f"User SMS: {'✅' if results['user_sms'] else '❌'}")
    print(f"Vendor Email: {'✅' if results['vendor_email'] else '❌'}")
    print(f"Vendor SMS: {'✅' if results['vendor_sms'] else '❌'}")
