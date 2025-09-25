"""
Batch sending script for reviewing and sending draft emails.
Reads saved emails from demo folder, allows user review, and sends via SendGrid.
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from src.email_service import EmailService, EmailFileManager
from src.config import Config, get_sendgrid_api_key, get_sender_email


class DraftEmailManager:
    """Manager class for handling draft email operations."""
    
    def __init__(self):
        """Initialize the draft email manager."""
        self.email_service = None
        self._initialize_email_service()
    
    def _initialize_email_service(self) -> None:
        """Initialize the email service with proper validation."""
        try:
            get_sendgrid_api_key()
            get_sender_email()
            self.email_service = EmailService()
            print("✅ SendGrid service initialized successfully")
        except ValueError as e:
            print(f"❌ Configuration Error: {e}")
            print("Please ensure SENDGRID_API_KEY and SENDER_EMAIL are set in your .env file.")
            sys.exit(1)
    
    def _display_email_content(self, email_data: Dict[str, Any], index: int, total: int) -> None:
        """
        Display email content in a formatted way.
        
        Args:
            email_data (Dict[str, Any]): Email data to display
            index (int): Current email index
            total (int): Total number of emails
        """
        print(f"\n{'='*60}")
        print(f"📧 DRAFT EMAIL {index}/{total}")
        print(f"={'='*60}")
        
        # Display metadata
        company_name = email_data.get('company_name', 'Unknown Company')
        generated_at = email_data.get('generated_at', 'Unknown time')
        print(f"🏢 Company: {company_name}")
        print(f"🕐 Generated: {generated_at}")
        
        # Display email content
        email_content = email_data.get('email', {})
        print(f"\n📬 To: {email_content.get('to_address', 'N/A')}")
        print(f"📋 Subject: {email_content.get('subject', 'N/A')}")
        print("\n📝 Body:")
        print("-" * 50)
        print(email_content.get('body', 'No content available'))
        print("-" * 50)
    
    def _get_user_confirmation(self) -> str:
        """
        Get user confirmation for sending the email.
        
        Returns:
            str: User choice ('y', 'n', or 'q')
        """
        while True:
            try:
                print("\n🤔 Options:")
                print("(y)es - Send this email")
                print("(n)o  - Skip this email")
                print("(q)uit - Exit the script")
                
                choice = input("Enter your choice (y/n/q): ").strip().lower()
                
                if choice in ['y', 'yes']:
                    return 'y'
                elif choice in ['n', 'no']:
                    return 'n'
                elif choice in ['q', 'quit']:
                    return 'q'
                else:
                    print("❌ Invalid choice. Please enter 'y', 'n', or 'q'.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return 'q'
    
    def _send_draft_email(self, email_data: Dict[str, Any], filepath: str) -> bool:
        """
        Send a draft email and handle file operations.
        
        Args:
            email_data (Dict[str, Any]): Email data to send
            filepath (str): Path to the draft file
            
        Returns:
            bool: True if successful, False otherwise
        """
        email_content = email_data.get('email', {})
        
        # Send the email
        print("\n📤 Sending email...")
        success = self.email_service.send_email(email_content)
        
        if success:
            # Move file from demo to real folder
            moved = EmailFileManager.move_file(filepath, Config.REAL_OUTPUT_DIR)
            if moved:
                print("✅ Email sent and file moved to 'real' folder")
                return True
            else:
                print("⚠️ Email sent but failed to move file")
                return False
        else:
            print("❌ Failed to send email")
            return False
    
    def process_draft_emails(self) -> None:
        """Process all draft emails in the demo folder."""
        print("🚀 Draft Email Batch Processor")
        print("=" * 50)
        
        # Get all draft files
        draft_files = EmailFileManager.get_demo_files()
        
        if not draft_files:
            print("📭 No draft emails found in the demo folder.")
            print(f"📁 Demo folder: {Config.DEMO_OUTPUT_DIR}")
            print("\n💡 Generate emails in demo mode first using: python main.py")
            return
        
        print(f"📧 Found {len(draft_files)} draft email(s) to review")
        
        sent_count = 0
        skipped_count = 0
        
        for i, filepath in enumerate(draft_files, 1):
            # Load email data
            email_data = EmailFileManager.load_email_from_file(filepath)
            
            if not email_data:
                print(f"❌ Failed to load email from: {filepath}")
                continue
            
            # Display email content
            self._display_email_content(email_data, i, len(draft_files))
            
            # Get user confirmation
            choice = self._get_user_confirmation()
            
            if choice == 'q':
                print("\n👋 Exiting batch processor...")
                break
            elif choice == 'y':
                # Send the email
                if self._send_draft_email(email_data, filepath):
                    sent_count += 1
                else:
                    print("⚠️ Email sending failed, keeping file in demo folder")
            else:  # choice == 'n'
                print("⏭️ Skipping this email...")
                skipped_count += 1
        
        # Display summary
        print(f"\n{'='*50}")
        print("📊 BATCH PROCESSING SUMMARY")
        print(f"{'='*50}")
        print(f"✅ Emails sent: {sent_count}")
        print(f"⏭️ Emails skipped: {skipped_count}")
        print(f"📁 Remaining drafts: {len(EmailFileManager.get_demo_files())}")
        print(f"{'='*50}")


class BatchSenderApp:
    """Main application class for batch sending draft emails."""
    
    def __init__(self):
        """Initialize the batch sender application."""
        self.draft_manager = None
    
    def _validate_environment(self) -> bool:
        """
        Validate SendGrid configuration.
        
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            get_sendgrid_api_key()
            get_sender_email()
            return True
        except ValueError as e:
            print(f"❌ Environment Error: {e}")
            print("This script requires SendGrid configuration to send emails.")
            print("Please ensure SENDGRID_API_KEY and SENDER_EMAIL are set in your .env file.")
            return False
    
    def run(self) -> None:
        """Main execution flow for batch sending."""
        print("📮 Agentic Email System - Draft Batch Sender")
        print("Review and send saved draft emails")
        print("=" * 60)
        
        # Validate environment
        if not self._validate_environment():
            sys.exit(1)
        
        try:
            # Initialize draft manager
            self.draft_manager = DraftEmailManager()
            
            # Process draft emails
            self.draft_manager.process_draft_emails()
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Process interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please check your configuration and try again.")
            sys.exit(1)


def main() -> None:
    """Application entry point."""
    app = BatchSenderApp()
    app.run()


if __name__ == "__main__":
    main()