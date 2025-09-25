"""
Main entry point for the Agentic Email Generation System - Version 2.
Provides demo and real modes with file saving and email sending capabilities.
"""

import json
import sys
from typing import Optional, Tuple
from src.graph import create_workflow
from src.config import get_tavily_api_key, get_sendgrid_api_key, get_sender_email
from src.email_service import EmailService, EmailFileManager


class EmailGeneratorApp:
    """Main application class for the email generation system - Version 2."""
    
    def __init__(self):
        """Initialize the application."""
        self.workflow = None
        self.email_service = None
    
    def _validate_environment(self, mode: str) -> bool:
        """
        Validate that all required environment variables are set for the selected mode.
        
        Args:
            mode (str): Selected mode ("demo", "manual_demo", or "real")
            
        Returns:
            bool: True if environment is valid, False otherwise
        """
        try:
            # Always validate Tavily API key for demo and real modes
            if mode in ["demo", "real"]:
                get_tavily_api_key()
            
            # Validate SendGrid credentials for manual_demo and real modes
            if mode in ["manual_demo", "real"]:
                get_sendgrid_api_key()
                get_sender_email()
                print("✅ SendGrid configuration validated")
            
            return True
        except ValueError as e:
            print(f"❌ Environment Error: {e}")
            if mode in ["manual_demo", "real"]:
                print("For manual demo and real modes, ensure SENDGRID_API_KEY and SENDER_EMAIL are set in your .env file.")
            else:
                print("Please check your .env file and ensure TAVILY_API_KEY is set.")
            return False
    
    def _get_mode_selection(self) -> Optional[str]:
        """
        Get user's mode selection (demo, manual_demo, or real).
        
        Returns:
            Optional[str]: Selected mode or None if invalid
        """
        print("\n🔧 SELECT OPERATING MODE")
        print("=" * 50)
        print("(d)emo        - Generate and save email locally using AI research")
        print("(m)anual_demo - Manually provide email & product, send via SendGrid") 
        print("(r)eal        - Generate and send email via SendGrid using AI research")
        print("=" * 50)
        
        try:
            choice = input("Choose mode (d/m/r): ").strip().lower()
            
            if choice in ['d', 'demo']:
                return "demo"
            elif choice in ['m', 'manual', 'manual_demo']:
                return "manual_demo"
            elif choice in ['r', 'real']:
                return "real"
            else:
                print("❌ Invalid choice. Please enter 'd' for demo, 'm' for manual demo, or 'r' for real mode.")
                return None
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return None
    
    def _get_company_input(self) -> Optional[str]:
        """
        Get and validate company name input from user.
        
        Returns:
            Optional[str]: Company name or None if invalid
        """
        try:
            company = input("\n📝 Enter the target company name: ").strip()
            
            if not company:
                print("❌ Company name cannot be empty.")
                return None
            
            if len(company) < 2:
                print("❌ Please enter a valid company name (at least 2 characters).")
                return None
            
            return company
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return None
    
    def _get_manual_demo_input(self) -> Optional[Tuple[str, str, str]]:
        """
        Get manual demo inputs: email address and product description.
        
        Returns:
            Optional[Tuple[str, str, str]]: (email, product_name, description) or None if invalid
        """
        try:
            print("\n📧 MANUAL DEMO MODE - Enter Details")
            print("=" * 40)
            
            # Get email address
            email = input("📬 Enter target email address: ").strip()
            if not email or '@' not in email:
                print("❌ Please enter a valid email address.")
                return None
            
            # Get product name
            product_name = input("🛍️ Enter your product/service name: ").strip()
            if not product_name:
                print("❌ Product name cannot be empty.")
                return None
            
            # Get product description
            print("📝 Enter product description (or press Enter for default):")
            description = input().strip()
            if not description:
                description = f"Our innovative {product_name} solution designed to help businesses achieve their goals more efficiently."
            
            return email, product_name, description
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return None
    
    def _handle_manual_demo_mode(self, target_email: str, product_name: str, description: str) -> None:
        """
        Handle manual demo mode operations (generate email with provided details and send).
        
        Args:
            target_email (str): Target email address
            product_name (str): Product/service name
            description (str): Product description
        """
        print("\n🛍️ MANUAL DEMO MODE: Generating personalized email...")
        
        # Generate email using simple LLM call (no agents needed for this)
        email_data = self._generate_manual_demo_email(target_email, product_name, description)
        
        # Display the generated email
        print("\n" + "="*60)
        print("📧 GENERATED MANUAL DEMO EMAIL")
        print("="*60)
        print(f"📬 To: {email_data.get('to_address', 'N/A')}")
        print(f"📋 Subject: {email_data.get('subject', 'N/A')}")
        print("\n📝 Body:")
        print("-" * 40)
        print(email_data.get('body', 'No content generated'))
        print("-" * 40)
        
        # Ask for confirmation before sending
        try:
            send_confirm = input("\n📤 Send this email now? (y/n): ").strip().lower()
            if send_confirm in ['y', 'yes']:
                # Initialize email service if not already done
                if not self.email_service:
                    self.email_service = EmailService()
                
                # Send email
                print("\n📧 Sending email via SendGrid...")
                success = self.email_service.send_email(email_data)
                
                if success:
                    # Save copy to demo directory (since this is a demo mode)
                    EmailFileManager.save_email_to_file(
                        email_data, f"Manual_Demo_{product_name}", mode="demo"
                    )
                    print("✅ Manual demo complete! Email sent and copy saved to demo folder.")
                else:
                    print("❌ Failed to send email. Please check your SendGrid configuration.")
            else:
                # Just save to demo folder without sending
                EmailFileManager.save_email_to_file(
                    email_data, f"Manual_Demo_{product_name}", mode="demo"
                )
                print("📁 Email saved to demo folder without sending.")
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Operation cancelled.")
    
    def _generate_manual_demo_email(self, target_email: str, product_name: str, description: str) -> dict:
        """
        Generate email content for manual demo mode.
        
        Args:
            target_email (str): Target email address
            product_name (str): Product name
            description (str): Product description
            
        Returns:
            dict: Generated email data
        """
        try:
            from .config import get_local_llm
            
            llm = get_local_llm()
            
            prompt = f"""
Write a professional B2B sales email for the following:

Target Email: {target_email}
Product/Service: {product_name}
Description: {description}

Create a compelling email that:
1. Has a professional, engaging subject line
2. Introduces the product/service clearly
3. Highlights key benefits and value proposition
4. Includes a clear call-to-action
5. Maintains a professional but friendly tone
6. Is concise (under 150 words in body)

Format your response as:
SUBJECT: [subject line]
BODY: [email body content]
"""
            
            response = llm.invoke(prompt)
            content = str(response.content) if hasattr(response, 'content') else str(response)
            
            # Parse the response
            lines = content.split('\n')
            subject = ""
            body_lines = []
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('SUBJECT:'):
                    subject = line.replace('SUBJECT:', '').strip()
                    current_section = 'subject'
                elif line.startswith('BODY:'):
                    current_section = 'body'
                    body_content = line.replace('BODY:', '').strip()
                    if body_content:
                        body_lines.append(body_content)
                elif current_section == 'body' and line:
                    body_lines.append(line)
            
            # Fallback if parsing fails
            if not subject:
                subject = f"Introducing {product_name} - Partnership Opportunity"
            
            if not body_lines:
                body_lines = [
                    f"Dear Colleague,",
                    f"",
                    f"I hope this email finds you well. I wanted to introduce you to {product_name}.",
                    f"",
                    f"{description}",
                    f"",
                    f"I believe this could be valuable for your business. Would you be interested in learning more?",
                    f"",
                    f"Best regards,",
                    f"[Your Name]"
                ]
            
            return {
                "to_address": target_email,
                "subject": subject,
                "body": '\n'.join(body_lines)
            }
            
        except Exception as e:
            print(f"⚠️ Error generating email content: {str(e)}")
            # Return fallback email
            return {
                "to_address": target_email,
                "subject": f"Introducing {product_name} - Partnership Opportunity",
                "body": f"Dear Colleague,\n\nI hope this email finds you well. I wanted to introduce you to {product_name}.\n\n{description}\n\nI believe this could be valuable for your business. Would you be interested in learning more?\n\nBest regards,\n[Your Name]"
            }
    
    def _handle_demo_mode(self, email_data: dict, company_name: str) -> None:
        """
        Handle demo mode operations (save to file).
        
        Args:
            email_data (dict): Generated email data
            company_name (str): Target company name
        """
        print("\n🔧 DEMO MODE: Saving email to file...")
        
        # Save email to demo directory
        filepath = EmailFileManager.save_email_to_file(
            email_data, company_name, mode="demo"
        )
        
        print(f"✅ Demo mode complete! Email saved for later review.")
        print(f"📁 File location: {filepath}")
        print("\n💡 Tip: Use 'python send_drafts.py' to review and send saved emails.")
    
    def _handle_real_mode(self, email_data: dict, company_name: str) -> None:
        """
        Handle real mode operations (send email and save copy).
        
        Args:
            email_data (dict): Generated email data
            company_name (str): Target company name
        """
        print("\n📧 REAL MODE: Sending email via SendGrid...")
        
        # Initialize email service if not already done
        if not self.email_service:
            self.email_service = EmailService()
        
        # Send email
        success = self.email_service.send_email(email_data)
        
        if success:
            # Save copy to real directory
            EmailFileManager.save_email_to_file(
                email_data, company_name, mode="real"
            )
            print("✅ Real mode complete! Email sent and copy saved.")
        else:
            print("❌ Failed to send email. Please check your SendGrid configuration.")
    
    def _display_results(self, final_state: dict, mode: str) -> dict:
        """
        Display the final email results and return email data.
        
        Args:
            final_state (dict): The final workflow state with generated email
            mode (str): Operating mode for context
            
        Returns:
            dict: Email data for further processing
        """
        print("\n" + "="*60)
        print(f"📧 GENERATED EMAIL ({mode.upper()} MODE)")
        print("="*60)
        
        final_email = final_state.get('final_email', {})
        
        if isinstance(final_email, dict) and final_email:
            # Display structured output
            print(f"📬 To: {final_email.get('to_address', 'N/A')}")
            print(f"📋 Subject: {final_email.get('subject', 'N/A')}")
            print("\n📝 Body:")
            print("-" * 40)
            print(final_email.get('body', 'No content generated'))
            print("-" * 40)
            
            return final_email
        else:
            print("❌ No email was generated. Please try again.")
            return {}
        """
        Handle demo mode operations (save to file).
        
        Args:
            email_data (dict): Generated email data
            company_name (str): Target company name
        """
        print("\n🔧 DEMO MODE: Saving email to file...")
        
        # Save email to demo directory
        filepath = EmailFileManager.save_email_to_file(
            email_data, company_name, mode="demo"
        )
        
        print(f"✅ Demo mode complete! Email saved for later review.")
        print(f"📁 File location: {filepath}")
        print("\n💡 Tip: Use 'python send_drafts.py' to review and send saved emails.")
    
    def _handle_real_mode(self, email_data: dict, company_name: str) -> None:
        """
        Handle real mode operations (send email and save copy).
        
        Args:
            email_data (dict): Generated email data
            company_name (str): Target company name
        """
        print("\n📧 REAL MODE: Sending email via SendGrid...")
        
        # Initialize email service if not already done
        if not self.email_service:
            self.email_service = EmailService()
        
        # Send email
        success = self.email_service.send_email(email_data)
        
        if success:
            # Save copy to real directory
            EmailFileManager.save_email_to_file(
                email_data, company_name, mode="real"
            )
            print("✅ Real mode complete! Email sent and copy saved.")
        else:
            print("❌ Failed to send email. Please check your SendGrid configuration.")
    
    def _display_results(self, final_state: dict, mode: str) -> dict:
        """
        Display the final email results and return email data.
        
        Args:
            final_state (dict): The final workflow state with generated email
            mode (str): Operating mode for context
            
        Returns:
            dict: Email data for further processing
        """
        print("\n" + "="*60)
        print(f"📧 GENERATED EMAIL ({mode.upper()} MODE)")
        print("="*60)
        
        final_email = final_state.get('final_email', {})
        
        if isinstance(final_email, dict) and final_email:
            # Display structured output
            print(f"📬 To: {final_email.get('to_address', 'N/A')}")
            print(f"📋 Subject: {final_email.get('subject', 'N/A')}")
            print("\n📝 Body:")
            print("-" * 40)
            print(final_email.get('body', 'No content generated'))
            print("-" * 40)
            
            return final_email
        else:
            print("❌ No email was generated. Please try again.")
            return {}
    
    def run(self) -> None:
        """Main application execution flow with mode selection."""
        print("🚀 Agentic Email Generation System - Version 2")
        print("Enhanced with Demo/Manual Demo/Real Modes and SendGrid Integration")
        print("="*70)
        
        # Get mode selection
        mode = self._get_mode_selection()
        if not mode:
            sys.exit(1)
        
        # Validate environment for selected mode
        if not self._validate_environment(mode):
            sys.exit(1)
        
        print(f"\n✅ {mode.upper()} mode selected")
        
        try:
            if mode == "manual_demo":
                # Handle manual demo mode
                manual_inputs = self._get_manual_demo_input()
                if not manual_inputs:
                    sys.exit(1)
                
                target_email, product_name, description = manual_inputs
                self._handle_manual_demo_mode(target_email, product_name, description)
                
            else:
                # Handle regular demo and real modes (with AI research)
                company_name = self._get_company_input()
                if not company_name:
                    sys.exit(1)
                
                # Initialize workflow
                print("\n⚙️ Initializing workflow...")
                self.workflow = create_workflow()
                
                # Execute workflow
                print(f"🤖 Starting multi-agent workflow for '{company_name}'...")
                print("This may take a few moments...\n")
                
                final_state = self.workflow.execute(company_name)
                
                # Display results and get email data
                email_data = self._display_results(final_state, mode)
                
                if not email_data:
                    sys.exit(1)
                
                # Handle mode-specific operations
                if mode == "demo":
                    self._handle_demo_mode(email_data, company_name)
                else:  # real mode
                    self._handle_real_mode(email_data, company_name)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Process interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ An error occurred: {str(e)}")
            print("Please check your configuration and try again.")
            sys.exit(1)


def main() -> None:
    """Application entry point."""
    app = EmailGeneratorApp()
    app.run()


if __name__ == "__main__":
    main()