"""
LangGraph workflow definition for the multi-agent email generation system.
Orchestrates the collaboration between Researcher, Strategist, and Copywriter agents.
"""

import re
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
from .agents import ResearchAgent, StrategistAgent, CopywriterAgent


class WorkflowState(TypedDict):
    """State object that flows between agents in the workflow."""
    company_name: str
    research_summary: str
    sales_hook: str
    final_email: Dict[str, Any]


def extract_best_email_from_research(research_text: str, company_name: str) -> str:
    """
    Extract the best business email address from research text.
    
    Args:
        research_text (str): Research summary containing contact info
        company_name (str): Company name for fallback
        
    Returns:
        str: Best email address found or fallback
    """
    # Look for priority-marked emails first
    priority_patterns = [
        r'🟢\s*HIGH PRIORITY[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'HIGH PRIORITY[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'🟡\s*MEDIUM PRIORITY[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
    ]
    
    for pattern in priority_patterns:
        matches = re.findall(pattern, research_text, re.IGNORECASE)
        if matches:
            return matches[0]
    
    # Look for specific business email patterns
    business_patterns = [
        r'(?i)sales[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'(?i)business[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'(?i)partnership[s]?[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'(?i)contact[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
        r'(?i)info[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',
    ]
    
    for pattern in business_patterns:
        matches = re.findall(pattern, research_text)
        if matches:
            return matches[0]
    
    # Look for any email with company domain
    company_clean = company_name.lower().replace(' ', '').replace('.', '')
    all_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', research_text)
    
    for email in all_emails:
        if company_clean in email.lower():
            return email
    
    # Return first valid email found, or fallback
    if all_emails:
        return all_emails[0]
    
    # Final fallback
    return f"contact@{company_clean}.com"


class WorkflowState(TypedDict):
    """State object that flows between agents in the workflow."""
    company_name: str
    research_summary: str
    sales_hook: str
    final_email: Dict[str, Any]


class WorkflowNodes:
    """Contains all node functions for the workflow graph."""
    
    @staticmethod
    def research_node(state: WorkflowState) -> Dict[str, str]:
        """
        Research node: Gathers information about the target company.
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            Dict[str, str]: Updated state with research summary
        """
        print("🔍 Research Agent: Starting company research...")
        
        # Create researcher agent
        researcher = ResearchAgent.create()
        
        # Prepare research input
        research_input = f"""
Research the company '{state['company_name']}' thoroughly and find their real contact information.

Your research should include:
1. Recent company news and developments
2. Business initiatives and growth areas  
3. Market position and opportunities
4. **MOST IMPORTANT**: Find real contact email addresses using the find_company_contact_info tool
5. Check the status of https://sendgrid.com/ as requested

Make sure to use the find_company_contact_info tool to get actual email addresses for business outreach.
Do not guess or make up email addresses - find real ones through research.

Focus on finding the most appropriate contact person/email for business partnerships or sales inquiries.
"""
        
        # Execute research
        result = researcher.invoke({"input": research_input})
        
        print("✅ Research Agent: Research completed")
        return {"research_summary": result['output']}
    
    @staticmethod
    def strategist_node(state: WorkflowState) -> Dict[str, str]:
        """
        Strategy node: Analyzes research and creates strategic sales hook.
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            Dict[str, str]: Updated state with sales hook
        """
        print("🎯 Strategist Agent: Analyzing research and creating sales hook...")
        
        # Create strategist agent
        strategist = StrategistAgent.create()
        
        # Prepare strategy input
        strategy_input = f"""
Based on the following research about {state['company_name']}, 
create a compelling sales hook:

RESEARCH DATA:
{state['research_summary']}

Create a strategic sales approach that:
1. Addresses a specific business need or opportunity
2. Positions our solution as valuable
3. Is tailored to their current situation
"""
        
        # Execute strategy development
        result = strategist.invoke({"input": strategy_input})
        
        print("✅ Strategist Agent: Sales hook created")
        return {"sales_hook": result['output']}
    
    @staticmethod
    def copywriter_node(state: WorkflowState) -> Dict[str, Dict[str, Any]]:
        """
        Copywriting node: Transforms strategy into professional email.
        
        Args:
            state (WorkflowState): Current workflow state
            
        Returns:
            Dict[str, Dict[str, Any]]: Updated state with final email
        """
        print("✍️ Copywriter Agent: Writing professional email...")
        
        # Create copywriter agent
        copywriter = CopywriterAgent.create()
        
        # Prepare copywriting input
        copywriting_input = f"""
Transform this strategic sales hook into a professional B2B email for {state['company_name']}:

SALES HOOK: {state['sales_hook']}

RESEARCH DATA (including contact information):
{state['research_summary']}

Create a professional email using the EmailOutput tool with:
- REAL to_address: Extract the actual email address from the research data above. Look for specific emails like sales@, partnerships@, business@, or contact@ with the real company domain. DO NOT make up generic emails.
- Compelling subject line (50-80 characters)
- Concise, engaging body (under 150 words)  
- Clear call-to-action
- Professional tone

CRITICAL: Use the real contact email found in the research data, not a made-up address.
"""
        
        try:
            # Invoke the copywriter agent
            result = copywriter.invoke({"input": copywriting_input})
            
            # The result should contain tool calls in the output
            output_text = result.get('output', '')
            
            # Look for tool calls in the agent's messages
            if hasattr(result, 'get') and 'messages' in str(result):
                # Try to extract from agent messages
                messages = result.get('messages', [])
                for message in messages:
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        tool_call = message.tool_calls[0]
                        if 'args' in tool_call:
                            email_dict = tool_call['args']
                            print("✅ Copywriter Agent: Email completed")
                            return {"final_email": email_dict}
            
            # Fallback: try to parse the output directly
            if isinstance(output_text, str) and 'to_address' in output_text:
                # If the output contains structured data, try to parse it
                import json
                try:
                    email_dict = json.loads(output_text)
                    print("✅ Copywriter Agent: Email completed")
                    return {"final_email": email_dict}
                except:
                    pass
            
            # Last fallback: create a basic structure
            raise ValueError("Could not extract structured email data from agent output")
                
        except Exception as e:
            print(f"❌ Error in copywriter: {str(e)}")
            # Fallback: extract email from research data
            extracted_email = extract_best_email_from_research(state['research_summary'], state['company_name'])
            
            email_dict = {
                "to_address": extracted_email,
                "subject": f"Partnership Opportunity - {state['company_name']}",
                "body": f"Dear {state['company_name']} Team,\n\n{state['sales_hook']}\n\nI'd love to discuss how we can work together to achieve your business goals.\n\nBest regards,\n[Your Name]"
            }
            
        print("✅ Copywriter Agent: Email completed")
        return {"final_email": email_dict}


class EmailWorkflow:
    """Main workflow orchestrator for the email generation process."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow with nodes and edges.
        
        Returns:
            StateGraph: Configured workflow graph
        """
        # Create workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("researcher", WorkflowNodes.research_node)
        workflow.add_node("strategist", WorkflowNodes.strategist_node)
        workflow.add_node("copywriter", WorkflowNodes.copywriter_node)
        
        # Define workflow edges (agent handoffs)
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "strategist")
        workflow.add_edge("strategist", "copywriter")
        workflow.add_edge("copywriter", END)
        
        return workflow
    
    def execute(self, company_name: str) -> WorkflowState:
        """
        Execute the complete email generation workflow.
        
        Args:
            company_name (str): Name of the target company
            
        Returns:
            WorkflowState: Final state with generated email
        """
        print(f"🚀 Starting workflow for: {company_name}")
        print("="*60)
        
        # Define initial state
        initial_state: WorkflowState = {
            "company_name": company_name,
            "research_summary": "",
            "sales_hook": "",
            "final_email": {}
        }
        
        # Execute workflow
        final_state = self.app.invoke(initial_state)
        
        print("="*60)
        print("✅ Workflow completed successfully!")
        
        return final_state


def create_workflow() -> EmailWorkflow:
    """
    Factory function to create a new email generation workflow.
    
    Returns:
        EmailWorkflow: Configured workflow instance
    """
    return EmailWorkflow()