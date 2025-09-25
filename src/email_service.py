"""
Email service module for sending emails via SendGrid API.
Handles email composition, sending, and logging functionality.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .config import get_sendgrid_api_key, get_sender_email, Config


class EmailService:
    """Service class for handling email operations with SendGrid."""
    
    def __init__(self):
        """Initialize the email service with SendGrid client."""
        self.api_key = get_sendgrid_api_key()
        self.sender_email = get_sender_email()
        self.sg_client = SendGridAPIClient(api_key=self.api_key)
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration for sent emails."""
        # Ensure logs directory exists
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.SENT_EMAILS_LOG),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, email_data: Dict[str, Any]) -> bool:
        """
        Send an email using SendGrid API.
        
        Args:
            email_data (Dict[str, Any]): Email data containing to_address, subject, body
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create mail object
            message = Mail(
                from_email=self.sender_email,
                to_emails=email_data['to_address'],
                subject=email_data['subject'],
                html_content=self._format_email_body(email_data['body'])
            )
            
            # Send email
            response = self.sg_client.send(message)
            
            # Check if email was sent successfully
            if response.status_code in [200, 201, 202]:
                self._log_sent_email(email_data)
                print(f"✅ Email sent successfully to {email_data['to_address']}")
                return True
            else:
                print(f"❌ Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def _format_email_body(self, body: str) -> str:
        """
        Format email body for HTML display.
        
        Args:
            body (str): Plain text email body
            
        Returns:
            str: HTML formatted email body
        """
        # Convert line breaks to HTML
        html_body = body.replace('\n', '<br>')
        
        # Wrap in basic HTML structure
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            {html_body}
        </body>
        </html>
        """
    
    def _log_sent_email(self, email_data: Dict[str, Any]) -> None:
        """
        Log sent email details to the log file.
        
        Args:
            email_data (Dict[str, Any]): Email data to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"SENT - {email_data['to_address']} - {timestamp} - Subject: {email_data['subject']}"
        self.logger.info(log_entry)


class EmailFileManager:
    """Manager class for handling email file operations."""
    
    @staticmethod
    def ensure_directories() -> None:
        """Create necessary directories if they don't exist."""
        os.makedirs(Config.DEMO_OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.REAL_OUTPUT_DIR, exist_ok=True)
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
    
    @staticmethod
    def save_email_to_file(
        email_data: Dict[str, Any], 
        company_name: str, 
        mode: str = "demo"
    ) -> str:
        """
        Save email data to a JSON file.
        
        Args:
            email_data (Dict[str, Any]): Email data to save
            company_name (str): Name of the target company
            mode (str): Either "demo" or "real"
            
        Returns:
            str: Path to the saved file
        """
        EmailFileManager.ensure_directories()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company_name = company_name.replace(" ", "_").replace("/", "_")
        filename = f"{safe_company_name}_{timestamp}.json"
        
        # Determine output directory
        output_dir = Config.DEMO_OUTPUT_DIR if mode == "demo" else Config.REAL_OUTPUT_DIR
        filepath = os.path.join(output_dir, filename)
        
        # Add metadata to email data
        email_with_metadata = {
            "company_name": company_name,
            "generated_at": datetime.now().isoformat(),
            "mode": mode,
            "email": email_data
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(email_with_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Email saved to: {filepath}")
        return filepath
    
    @staticmethod
    def load_email_from_file(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load email data from a JSON file.
        
        Args:
            filepath (str): Path to the JSON file
            
        Returns:
            Optional[Dict[str, Any]]: Email data or None if error
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading email from {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def move_file(source_path: str, destination_dir: str) -> bool:
        """
        Move a file from source to destination directory.
        
        Args:
            source_path (str): Source file path
            destination_dir (str): Destination directory
            
        Returns:
            bool: True if moved successfully, False otherwise
        """
        try:
            import shutil
            filename = os.path.basename(source_path)
            destination_path = os.path.join(destination_dir, filename)
            shutil.move(source_path, destination_path)
            print(f"📦 Moved file to: {destination_path}")
            return True
        except Exception as e:
            print(f"❌ Error moving file: {str(e)}")
            return False
    
    @staticmethod
    def get_demo_files() -> list:
        """
        Get all email files from the demo directory.
        
        Returns:
            list: List of file paths in demo directory
        """
        EmailFileManager.ensure_directories()
        demo_files = []
        
        if os.path.exists(Config.DEMO_OUTPUT_DIR):
            for filename in os.listdir(Config.DEMO_OUTPUT_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(Config.DEMO_OUTPUT_DIR, filename)
                    demo_files.append(filepath)
        
        return sorted(demo_files)