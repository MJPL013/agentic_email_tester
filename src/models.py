"""
Pydantic models for structured data validation and output formatting.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class EmailOutput(BaseModel):
    """
    Structured output model for the final email generation.
    Ensures the LLM provides valid, well-formatted email content.
    """
    
    to_address: str = Field(
        description="The recipient's email address (e.g., 'contact@company.com')",
        example="contact@example.com"
    )
    
    subject: str = Field(
        description="The email subject line - should be compelling and relevant",
        min_length=5,
        max_length=100,
        example="Partnership Opportunity with [Company Name]"
    )
    
    body: str = Field(
        description="The complete email body content",
        min_length=50,
        example="Dear [Recipient],\n\nI hope this email finds you well..."
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "to_address": "contact@techcorp.com",
                "subject": "Strategic Partnership Opportunity",
                "body": "Dear TechCorp Team,\n\nI noticed your recent expansion into AI solutions..."
            }
        }