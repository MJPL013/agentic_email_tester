"""
Configuration module for the agentic email generation system.
Handles environment variables and LLM initialization.
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables at module import
load_dotenv()


class Config:
    """Central configuration class for the application."""
    
    # Ollama configuration
    OLLAMA_MODEL = "llama3.2"
    OLLAMA_BASE_URL = "http://localhost:11434/v1"
    OLLAMA_API_KEY = "ollama"  # Dummy key required by the library
    
    # LLM parameters
    LLM_TEMPERATURE = 0.1
    LLM_MAX_TOKENS = 4000
    
    # File paths
    BASE_DIR = r"E:\AGENTIC_AI\Day4\activity"
    DEMO_OUTPUT_DIR = os.path.join(BASE_DIR, "output_draft_emails", "demo")
    REAL_OUTPUT_DIR = os.path.join(BASE_DIR, "output_draft_emails", "real")
    LOGS_DIR = os.path.join(BASE_DIR, "logs")
    SENT_EMAILS_LOG = os.path.join(LOGS_DIR, "sent_emails.log")


def get_tavily_api_key() -> str:
    """
    Retrieve Tavily API key from environment variables.
    
    Returns:
        str: The Tavily API key
        
    Raises:
        ValueError: If the API key is not found
    """
    api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY not found in environment variables. "
            "Please add it to your .env file."
        )
    
    return api_key


def get_sendgrid_api_key() -> str:
    """
    Retrieve SendGrid API key from environment variables.
    
    Returns:
        str: The SendGrid API key
        
    Raises:
        ValueError: If the API key is not found
    """
    api_key: Optional[str] = os.getenv("SENDGRID_API_KEY")
    
    if not api_key:
        raise ValueError(
            "SENDGRID_API_KEY not found in environment variables. "
            "Please add it to your .env file."
        )
    
    return api_key


def get_sender_email() -> str:
    """
    Retrieve sender email from environment variables.
    
    Returns:
        str: The sender email address
        
    Raises:
        ValueError: If the sender email is not found
    """
    sender_email: Optional[str] = os.getenv("SENDER_EMAIL")
    
    if not sender_email:
        raise ValueError(
            "SENDER_EMAIL not found in environment variables. "
            "Please add it to your .env file."
        )
    
    return sender_email


def get_local_llm() -> ChatOpenAI:
    """
    Initialize and return the local LLM client configured for Ollama.
    
    Returns:
        ChatOpenAI: Configured LLM client
    """
    return ChatOpenAI(
        model=Config.OLLAMA_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        api_key=Config.OLLAMA_API_KEY,
        temperature=Config.LLM_TEMPERATURE,
        max_tokens=Config.LLM_MAX_TOKENS
    )