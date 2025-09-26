# Agentic Email Generation System - Version 2

🚀 **Multi-Agent Email Generation with Demo/Real Modes and SendGrid Integration**

An advanced Python application that uses multiple AI agents (Researcher, Strategist, Copywriter) to generate targeted sales emails. Version 2 introduces dual operating modes, file management, and automated email sending capabilities.

## 🆕 New Features in Version 2

### 🔧 **Dual Operating Modes**
- **Demo Mode**: Generate and save emails locally for review
- **Real Mode**: Generate and immediately send emails via SendGrid

### 📁 **File Management System**
- Automatic saving of generated emails with timestamps
- Organized folder structure for drafts and sent emails
- JSON format for easy data manipulation

### 📧 **SendGrid Integration**
- Professional email sending via SendGrid API
- HTML formatting for better presentation
- Comprehensive logging of sent emails

### 📦 **Batch Processing**
- Review and send multiple draft emails at once
- User confirmation for each email before sending
- Automatic file organization after sending

## 📋 Prerequisites

1. **Python 3.11+**
2. **Ollama with llama3.2 model** running locally
3. **Tavily API key** (free tier available)
4. **SendGrid API key** (for real mode and batch sending)

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file with your API keys:
```env
# Tavily API Key - Get from https://app.tavily.com/
TAVILY_API_KEY=your_tavily_api_key_here

# SendGrid API Key - Get from https://sendgrid.com/
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Verified sender email in SendGrid
SENDER_EMAIL=your_verified_sender@yourdomain.com
```



### 3. Verify Ollama Setup
Ensure Ollama is running with the llama3.2 model:
```bash
ollama run llama3.2
```

## 🎯 Usage

### Main Application - Email Generation

```bash
python main.py
```

**Mode Selection:**
- Choose `(d)emo` - Generate and save email locally using AI research
- Choose `(m) anual_demo` - manually provide email & product, send via SendGrid
- Choose `(r)eal` - Generate and send email via SendGrid using AI research




**Demo Mode Workflow:**
1. Select demo mode
2. Enter target company name
3. AI agents research and generate email
4. Email saved to `output_draft_emails/demo/`
5. Review later using batch sender

**Demo Mode Workflow:**
1. Select manual_demo mode
2. Enter sender email, target company name, and product name
3. AI agents generate email
4. Email saved to `output_draft_emails/demo/`
5. Review later using batch sender

**Real Mode Workflow:**
1. Select real mode
2. Enter target company name
3. AI agents research and generate email
4. Email sent immediately via SendGrid
5. Copy saved to `output_draft_emails/real/`
6. Action logged in `logs/sent_emails.log`

### Batch Sender - Review and Send Drafts

```bash
python send_drafts.py
```

**Batch Sending Features:**
- Reviews all emails in demo folder
- Displays full email content for each draft
- User confirmation required for each email
- Automatic file movement after successful sending
- Comprehensive sending summary

## 📂 Project Structure

```
E:\AGENTIC_AI\Day4\activity\
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── main.py                       # Main application entry point
├── send_drafts.py                # Batch email sender
├── README.md                  # This documentation
│
├── src/                          # Source code package
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Configuration management
│   ├── models.py                 # Pydantic data models
│   ├── tools.py                  # Agent tools (web search, status check)
│   ├── agents.py                 # Agent definitions
│   ├── graph.py                  # LangGraph workflow
│   └── email_service.py          # SendGrid email service
│
├── output_draft_emails/          # Generated emails storage
│   ├── demo/                     # Draft emails for review
│   └── real/                     # Copies of sent emails
│
└── logs/                         # Application logs
    └── sent_emails.log           # Email sending history
```

## 🤖 Agent Architecture

### 1. **Research Agent**
- Web research using Tavily API
- Service status checking
- Company intelligence gathering
- Recent news and developments analysis

### 2. **Strategist Agent** 
- Research data analysis
- Strategic sales hook creation
- Value proposition identification
- Business opportunity assessment

### 3. **Copywriter Agent**
- Professional email composition
- Structured output generation
- Tone and style optimization
- Call-to-action integration

## 📊 File Formats

### Generated Email JSON Structure
```json
{
  "company_name": "Target Company",
  "generated_at": "2024-01-15T10:30:00",
  "mode": "demo",
  "email": {
    "to_address": "contact@company.com",
    "subject": "Strategic Partnership Opportunity",
    "body": "Professional email content..."
  }
}
```

### Log File Format
```
2024-01-15 10:30:45 - INFO - SENT - contact@company.com - 2024-01-15 10:30:45 - Subject: Partnership Opportunity
```

## 🔒 Security Features

- Environment variables for API keys
- Git ignore for sensitive files
- Secure SendGrid API integration
- Comprehensive error handling
- Input validation and sanitization

## 🚦 Error Handling

The application includes robust error handling for:
- Missing API keys or configuration
- Network connectivity issues
- File system permissions
- SendGrid API errors
- Invalid user inputs

## 📈 Monitoring & Logging

- **Console Output**: Real-time progress updates
- **File Logging**: Persistent email sending history
- **Status Tracking**: Success/failure monitoring
- **File Organization**: Automatic draft/sent separation

## 🛡️ Best Practices

1. **Test in Demo Mode First**: Always test email generation before real sends
2. **Review Drafts Carefully**: Use batch sender to review content
3. **Monitor Logs**: Check sent_emails.log for sending history
4. **Backup Important Emails**: Keep copies of successful campaigns
5. **API Key Security**: Never commit .env files to version control

## 🔧 Troubleshooting

### Common Issues:

**"TAVILY_API_KEY not found"**
- Ensure .env file exists with correct API key
- Check file is in project root directory

**"Failed to send email"**
- Verify SendGrid API key is valid
- Confirm sender email is verified in SendGrid
- Check internet connectivity

**"No draft emails found"**
- Run main.py in demo mode first
- Check demo folder path exists

**Agent execution errors**
- Ensure Ollama is running with llama3.2
- Verify localhost:11434 is accessible

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files for detailed errors
3. Verify all prerequisites are installed
4. Ensure API keys have proper permissions

---

**Version 2.0** - Enhanced with dual modes, SendGrid integration, and batch processing capabilities.
