"""
Tools module containing all agent-usable tools.
Provides web search and service status checking capabilities.
"""

import requests
import re
from typing import List
from langchain_core.tools import tool
from tavily import TavilyClient
from .config import get_tavily_api_key


@tool
def check_service_status(url: str) -> str:
    """
    Check the HTTP status of a website or service.
    
    Args:
        url (str): The URL to check (e.g., 'https://example.com')
        
    Returns:
        str: Status message indicating the service availability
    """
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return f"✅ Success! {url} is online (Status: {response.status_code})"
        elif response.status_code == 202:
            return f"✅ Accepted! {url} returned status 202 (Request accepted)"
        else:
            return f"⚠️ {url} returned status {response.status_code}"
            
    except requests.exceptions.Timeout:
        return f"⏰ Timeout: {url} did not respond within 10 seconds"
    except requests.exceptions.ConnectionError:
        return f"🔌 Connection Error: Unable to reach {url}"
    except Exception as e:
        return f"❌ Error checking {url}: {str(e)}"


@tool
def web_search(query: str) -> str:
    """
    Perform a web search using the Tavily API to find recent and relevant information.
    
    Args:
        query (str): The search query (e.g., 'company news 2024')
        
    Returns:
        str: Formatted search results with relevant content
    """
    try:
        tavily_client = TavilyClient(api_key=get_tavily_api_key())
        
        # Perform search with optimized parameters
        search_results = tavily_client.search(
            query=query,
            max_results=3,
            search_depth="advanced"
        )
        
        if not search_results.get('results'):
            return f"No search results found for query: '{query}'"
        
        # Format results for LLM consumption
        formatted_results = []
        for i, result in enumerate(search_results['results'], 1):
            formatted_result = f"""
Result {i}:
Title: {result.get('title', 'N/A')}
Content: {result.get('content', 'No content available')}
URL: {result.get('url', 'N/A')}
"""
            formatted_results.append(formatted_result.strip())
        
        return "\n" + "="*50 + "\n".join(formatted_results) + "\n" + "="*50
        
    except Exception as e:
        return f"❌ Search error: {str(e)}"


@tool
def find_company_contact_info(company_name: str) -> str:
    """
    Search for company contact information including real email addresses from their website and contact pages.
    
    Args:
        company_name (str): The name of the company to find contact info for
        
    Returns:
        str: Contact information found for the company with real email addresses
    """
    try:
        tavily_client = TavilyClient(api_key=get_tavily_api_key())
        
        # Enhanced search queries to find real contact information
        contact_queries = [
            f"{company_name} official website contact page",
            f"{company_name} contact us email address",
            f"{company_name} support email customer service",
            f"{company_name} sales team contact information",
            f"{company_name} business inquiries email address",
            f"site:{company_name.lower().replace(' ', '')}.com contact",
            f"site:{company_name.lower().replace(' ', '')}.in contact",
            f"{company_name} partnerships email business development"
        ]
        
        all_found_emails = set()  # Use set to avoid duplicates
        all_contact_info = []
        
        for query in contact_queries:
            try:
                print(f"🔍 Searching: {query}")
                search_results = tavily_client.search(
                    query=query,
                    max_results=3,
                    search_depth="advanced"
                )
                
                if search_results.get('results'):
                    for result in search_results['results']:
                        content = result.get('content', '')
                        url = result.get('url', '')
                        title = result.get('title', '')
                        
                        # Enhanced email extraction with multiple patterns
                        email_patterns = [
                            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Standard emails
                            r'(?i)email[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # "Email: xxx@yyy.com"
                            r'(?i)contact[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # "Contact: xxx@yyy.com"
                            r'(?i)support[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # "Support: xxx@yyy.com"
                            r'(?i)sales[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',    # "Sales: xxx@yyy.com"
                        ]
                        
                        found_emails = set()
                        for pattern in email_patterns:
                            matches = re.findall(pattern, content)
                            if isinstance(matches, list) and matches:
                                for match in matches:
                                    if isinstance(match, tuple):
                                        found_emails.add(match[0])  # From groups
                                    else:
                                        found_emails.add(match)     # Direct match
                        
                        # Filter out common non-business emails and add to main set
                        business_emails = set()
                        for email in found_emails:
                            email_lower = email.lower()
                            # Skip common non-business email patterns
                            skip_patterns = [
                                'example.com', 'test.com', 'demo.com', 'placeholder.com',
                                'yourcompany.com', 'company.com', 'yourdomain.com',
                                'noreply@', 'no-reply@', 'donotreply@'
                            ]
                            
                            if not any(skip in email_lower for skip in skip_patterns):
                                # Prioritize emails that match the company domain
                                company_clean = company_name.lower().replace(' ', '').replace('.', '')
                                if company_clean in email_lower or any(domain in email_lower for domain in ['.com', '.in', '.org', '.net']):
                                    business_emails.add(email)
                                    all_found_emails.add(email)
                        
                        if business_emails or 'contact' in content.lower():
                            contact_entry = f"""
Source: {title}
URL: {url}
Found Business Emails: {', '.join(sorted(business_emails)) if business_emails else 'None in this snippet'}
Content Preview: {content[:400]}...
{'='*50}"""
                            all_contact_info.append(contact_entry.strip())
                            
            except Exception as e:
                print(f"⚠️ Error with query '{query}': {str(e)}")
                continue  # Try next query if this one fails
        
        # Analyze and rank found emails
        if all_found_emails:
            ranked_emails = _rank_business_emails(list(all_found_emails), company_name)
            
            return f"""
🎯 REAL CONTACT INFORMATION FOUND FOR {company_name.upper()}:
{'='*70}

📧 DISCOVERED EMAIL ADDRESSES:
{_format_email_list(ranked_emails)}

🔍 DETAILED SEARCH RESULTS:
{chr(10).join(all_contact_info[:3])}  
{'='*70}

✅ RECOMMENDATION: Use the highest-priority email from the list above.
These are real email addresses extracted from company websites and official sources.

⚠️ IMPORTANT: Always verify email addresses are current before sending important communications.
"""
        else:
            return f"""
⚠️ No specific business email addresses found for {company_name} in search results.

📋 SEARCH ATTEMPTED:
- Official website contact pages
- Customer support information  
- Business development contacts
- Sales team information

🔧 MANUAL VERIFICATION NEEDED:
1. Visit the company's official website directly
2. Check their 'Contact Us' or 'About' pages
3. Look for investor relations or media contacts
4. Consider LinkedIn outreach to find the right person

📧 FALLBACK OPTIONS:
- info@{company_name.lower().replace(' ', '')}.com
- contact@{company_name.lower().replace(' ', '')}.com
- sales@{company_name.lower().replace(' ', '')}.com

⚠️ Note: These fallback emails are generic guesses - verify they exist before sending.
"""
            
    except Exception as e:
        return f"❌ Error finding contact info for {company_name}: {str(e)}"


def _rank_business_emails(emails, company_name):
    """
    Rank business emails by priority/relevance.
    
    Args:
        emails (list): List of found email addresses
        company_name (str): Company name for relevance scoring
        
    Returns:
        list: Ranked list of emails with priority labels
    """
    ranked = []
    company_clean = company_name.lower().replace(' ', '').replace('.', '')
    
    # Priority categories
    high_priority = []      # sales@, business@, partnerships@, contact@
    medium_priority = []    # info@, hello@, support@ (if business context)
    low_priority = []       # other emails
    
    for email in emails:
        email_lower = email.lower()
        local_part = email_lower.split('@')[0]  # Part before @
        
        # High priority business emails
        if any(prefix in local_part for prefix in ['sales', 'business', 'partnership', 'contact', 'bd', 'bizdev']):
            high_priority.append(f"🟢 HIGH PRIORITY: {email}")
        # Medium priority
        elif any(prefix in local_part for prefix in ['info', 'hello', 'general', 'inquiry']):
            medium_priority.append(f"🟡 MEDIUM PRIORITY: {email}")
        # Company domain match gets higher priority
        elif company_clean in email_lower:
            high_priority.append(f"🟢 COMPANY DOMAIN: {email}")
        else:
            low_priority.append(f"🔵 STANDARD: {email}")
    
    # Combine in priority order
    ranked.extend(high_priority)
    ranked.extend(medium_priority)
    ranked.extend(low_priority)
    
    return ranked


def _format_email_list(ranked_emails):
    """Format the ranked email list for display."""
    if not ranked_emails:
        return "None found"
    
    formatted = []
    for i, email in enumerate(ranked_emails, 1):
        formatted.append(f"{i}. {email}")
    
    return '\n'.join(formatted)


class ToolManager:
    """Manager class for organizing and providing tools to agents."""
    
    @staticmethod
    def get_research_tools() -> List:
        """Get tools available for the researcher agent."""
        return [check_service_status, web_search, find_company_contact_info]
    
    @staticmethod
    def get_strategist_tools() -> List:
        """Get tools available for the strategist agent."""
        return []  # Strategist works with provided research data
    
    @staticmethod
    def get_copywriter_tools() -> List:
        """Get tools available for the copywriter agent."""
        return []  # Copywriter works with provided strategy data
    
    @staticmethod
    def get_all_tools() -> List:
        """Get all available tools."""
        return [check_service_status, web_search, find_company_contact_info]