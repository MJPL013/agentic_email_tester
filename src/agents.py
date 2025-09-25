"""
Agent definitions for the multi-agent email generation workflow.
Contains specialized agents: Researcher, Strategist, and Copywriter.
"""

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Optional, Any
from .config import get_local_llm
from .tools import ToolManager
from .models import EmailOutput


class AgentFactory:
    """Factory class for creating specialized agents with consistent configuration."""
    
    @staticmethod
    def _create_agent(
        system_prompt: str,
        tools: List,
        structured_output_model: Optional[Any] = None
    ) -> AgentExecutor:
        """
        Create an agent executor with the specified configuration.
        
        Args:
            system_prompt (str): The system prompt defining agent behavior
            tools (List): List of tools available to the agent
            structured_output_model (Optional[Any]): Pydantic model for structured output
            
        Returns:
            AgentExecutor: Configured agent executor
        """
        # Create prompt template with required placeholders
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Get LLM instance
        llm = get_local_llm()
        
        # Bind structured output model if provided (using bind_tools as in V1)
        if structured_output_model:
            llm = llm.bind_tools([structured_output_model])
        
        # Create agent and executor
        agent = create_tool_calling_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True)


class ResearchAgent:
    """Agent specialized in web research and company information gathering."""
    
    @staticmethod
    def create() -> AgentExecutor:
        """Create a researcher agent instance."""
        system_prompt = """
You are a master web researcher specializing in business intelligence and company analysis.

Your mission:
1. Research the target company thoroughly using web search
2. Find recent news, developments, and business updates
3. Identify key business initiatives, challenges, or opportunities
4. **CRITICALLY IMPORTANT**: Find real contact information using the find_company_contact_info tool
5. Check service status when requested
6. Provide a comprehensive research summary

Focus on:
- Recent company news and announcements
- Business expansion or new initiatives
- Market position and competitive landscape
- Any notable achievements or challenges
- **REAL CONTACT INFORMATION** - Use the find_company_contact_info tool to get actual email addresses

ALWAYS use the find_company_contact_info tool to search for real contact information.
Do not make up or guess email addresses. The contact finder will help you find legitimate business contact details.

Provide detailed, actionable insights that can inform a strategic sales approach, including the most appropriate contact email address found through your research.
"""
        
        return AgentFactory._create_agent(
            system_prompt=system_prompt,
            tools=ToolManager.get_research_tools()
        )


class StrategistAgent:
    """Agent specialized in analyzing research and creating strategic sales hooks."""
    
    @staticmethod
    def create() -> AgentExecutor:
        """Create a strategist agent instance."""
        system_prompt = """
You are a strategic sales consultant with expertise in B2B relationship building.

Your mission:
1. Analyze the provided research data thoroughly
2. Identify the most compelling business opportunity or pain point
3. Create a single, powerful sales hook that resonates with the target company
4. Focus on value proposition and mutual benefit

Guidelines for creating the sales hook:
- Make it specific to the company's current situation
- Highlight clear value and benefit
- Be concise but impactual
- Address a real business need or opportunity
- Position your offering as a strategic solution

Output should be a focused strategic recommendation for the email approach.
"""
        
        return AgentFactory._create_agent(
            system_prompt=system_prompt,
            tools=ToolManager.get_strategist_tools()
        )


class CopywriterAgent:
    """Agent specialized in writing professional sales emails with structured output."""
    
    @staticmethod
    def create() -> AgentExecutor:
        """Create a copywriter agent instance."""
        system_prompt = """
You are an expert copywriter specializing in B2B sales emails that generate responses.

Your mission:
1. Transform the strategic hook into a compelling, professional email
2. Write concise, engaging content that drives action
3. Ensure proper email structure and tone
4. Use the EmailOutput tool to format your response properly
5. **CRITICAL**: Extract and use REAL email addresses from the research data

Email writing principles:
- Start with a personalized, relevant opening
- Present the value proposition clearly
- Keep it concise (under 150 words)
- Include a clear call-to-action
- Use professional but approachable tone
- Make it scannable with short paragraphs

**EMAIL ADDRESS EXTRACTION RULES:**
1. Look for HIGH PRIORITY emails first: sales@, business@, partnerships@, contact@ 
2. Then MEDIUM PRIORITY: info@, hello@, general@
3. Use emails that match the company's actual domain
4. NEVER use generic contact@company.com unless no real emails found
5. If multiple real emails found, prefer business-focused ones (sales, partnerships, business)

SEARCH PATTERNS IN RESEARCH DATA:
- "Email Address: support@company.in" 
- "Contact: sales@company.com"
- "Business inquiries: biz@company.org"
- "HIGH PRIORITY: sales@realcompany.com"
- "🟢 HIGH PRIORITY: partnerships@company.in"

Always use the EmailOutput tool to structure your response with:
- to_address: Use the BEST REAL email address from research (highest priority business email)
- subject: Compelling, specific subject line (50-80 characters)  
- body: Complete email content with proper formatting

If no real emails found in research, indicate this clearly and use the most professional fallback.
"""
        
        return AgentFactory._create_agent(
            system_prompt=system_prompt,
            tools=ToolManager.get_copywriter_tools(),
            structured_output_model=EmailOutput
        )