import json
from typing import Dict, Any, List
from langchain_core.tools import tool
from app.core.config import settings

# In a real production setup, we would initialize the TavilyClient here
# from tavily import TavilyClient
# tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

@tool("tool_lead_generator")
def tool_lead_generator(icp: str) -> str:
    """
    Search the web for companies fitting the Ideal Customer Profile (ICP).
    Returns a JSON string formatted as a list of company names.
    """
    import json
    print(f"[Tool] Searching for companies matching ICP: {icp}...")
    
    if not settings.TAVILY_API_KEY or settings.TAVILY_API_KEY == "mock":
        # Fallback if no Tavily key
        return json.dumps(["Acme Corp", "Pinnacle Technologies", "NovaTech Solutions"])

    try:
        from tavily import TavilyClient
        from langchain_groq import ChatGroq
        from langchain_core.prompts import PromptTemplate
        
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        search_query = f"top {icp} companies software platform list 2024"
        response = client.search(query=search_query, max_results=5)
        
        search_context = "\n".join([res['content'] for res in response['results']])
        
        # Use LLM to extract clean list of company names from search context
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "mock":
            return json.dumps(["Mocked Domain 1", "Mocked Domain 2"])
            
        llm = ChatGroq(
            temperature=0.1,
            model_name="llama-3.3-70b-versatile", 
            api_key=settings.GROQ_API_KEY
        )
        
        prompt = PromptTemplate.from_template(
            """Extract exactly 3 to 5 real company names from the search context below that match the ICP '{icp}'.
            Return ONLY a raw JSON array of strings containing the company names. Do not include markdown formatting or the word json.
            
            Context:
            {context}
            """
        )
        
        chain = prompt | llm
        llm_resp = chain.invoke({"icp": icp, "context": search_context})
        
        # Clean the output to ensure valid JSON (remove backticks if any)
        clean_json = llm_resp.content.replace("```json", "").replace("```", "").strip()
        
        # Verify it parses, otherwise fallback
        names = json.loads(clean_json)
        if isinstance(names, list) and len(names) > 0:
             return json.dumps(names)
        else:
             raise ValueError("LLM did not return a valid list.")
             
    except Exception as e:
        print(f"[Tool] Error discovering leads: {e}")
        return json.dumps(["Acme Corp", "Apex Innovations", "Zenith Technologies"])

import urllib.request
import urllib.parse

@tool("tool_contact_finder")
def tool_contact_finder(company_name: str) -> str:
    """
    Fetch the most relevant contact email for a given company name.
    """
    import json
    import random
    import re
    print(f"[Tool] Discovering contacts for: {company_name}...")
    
    # Fallback/Mock logic if no Hunter.io key
    if not settings.HUNTER_API_KEY or settings.HUNTER_API_KEY == "mock":
        domain = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        if not domain:
            domain = "example"
        formats = [f"contact@{domain}.com", f"ceo@{domain}.com", f"sales@{domain}.com"]
        return random.choice(formats)
        
    try:
        # Use Hunter API Domain Search endpoint with 'company' query parameter
        encoded_company = urllib.parse.quote(company_name)
        url = f"https://api.hunter.io/v2/domain-search?company={encoded_company}&api_key={settings.HUNTER_API_KEY}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
             data = json.loads(response.read().decode())
             
        emails = data.get("data", {}).get("emails", [])
        if emails:
             # Just return the first (most confident) email
             return emails[0].get("value")
        else:
             raise ValueError("Hunter.io returned 0 emails for this company.")
             
    except Exception as e:
        print(f"[Tool] Error pulling from Hunter.io: {e}")
        domain = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower()) or "example"
        return f"info@{domain}.com"

@tool("tool_signal_harvester")
def tool_signal_harvester(company_name: str) -> str:
    """
    Fetch real company signals such as funding news, hiring trends, leadership changes,
    tech stack, and news mentions for the given company.
    
    Args:
        company_name (str): The name of the company to harvest signals for.
        
    Returns:
        str: JSON string containing the company name and a list of harvested signals.
    """
    print(f"[Tool] Harvesting signals for {company_name}...")
    
    # In a production environment, this is where we would call NewsAPI, SerpAPI, BuiltWith,
    # or Crunchbase. For this functional prototype, we'll simulate the response if the 
    # API keys are missing to ensure the system is end-to-end testable immediately.
    
    # Try using Tavily if key is available:
    if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY != "mock":
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(
                query=f"{company_name} funding OR hiring OR expansion OR product launch OR leadership change OR Series funding OR market expansion OR engineering hiring",
                search_depth="advanced",
                max_results=5
            )
            signals = [res['content'] for res in response['results']]
        except Exception as e:
             signals = [f"Error fetching real signals: {e}"]
    else:
        # Mock payload representing real-world signals for testing the prototype
        signals = [
            f"{company_name} recently secured a $15M Series B funding round.",
            "Hiring trends indicate a 20% increase in engineering roles over the last quarter.",
            "Recent leadership change: new VP of Sales hired to expand enterprise focus.",
            "Tech stack analysis shows active usage of React, Next.js, and Snowflake.",
            f"News mention: {company_name} announces expansion into the European market."
        ]
        
    result = {
        "company": company_name,
        "signals": signals
    }
    
    return json.dumps(result)

@tool("tool_research_analyst")
def tool_research_analyst(icp: str, signals: str) -> str:
    """
    Analyzes the harvested company signals against the Ideal Customer Profile (ICP)
    to generate a two-paragraph account brief explaining company growth signals,
    why the ICP is relevant, and potential business pain points.
    
    Args:
        icp (str): The Ideal Customer Profile.
        signals (str): JSON string containing the harvested company signals.
        
    Returns:
        str: A two-paragraph account brief.
    """
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    print(f"[Tool] Analyzing signals against ICP: {icp}...")
    
    # Parse signals to ensure it's valid
    try:
        signals_data = json.loads(signals)
        signals_list = signals_data.get("signals", [])
        company = signals_data.get("company", "the target company")
    except json.JSONDecodeError:
        signals_list = [signals]
        company = "the target company"
    
    prompt = PromptTemplate.from_template(
        """You are an expert sales researcher. Based on the following harvested signals 
        about {company} and the provided Ideal Customer Profile (ICP), generate a concise 
        TWO-PARAGRAPH account brief.
        
        Paragraph 1 MUST explain the company's recent growth signals (funding, hiring, market expansion).
        Paragraph 2 MUST explain why the ICP is relevant to them and identify their likely business pain points.
        
        Company: {company}
        ICP: {icp}
        Harvested Signals:
        {signals}
        
        Account Brief (strictly two paragraphs):"""
    )
    
    try:
        # Require Groq API key for the LLM reasoning
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "mock":
            return (
                f"Based on recent signals, {company} is experiencing significant growth, highlighted by their "
                f"recent $15M Series B funding and a 20% surge in engineering hiring. Their expansion into the "
                f"European market and new VP of Sales suggest a strong push for enterprise acquisition.\n\n"
                f"Given our ICP of '{icp}', {company} is an ideal fit. Their rapid expansion likely introduces "
                f"growing pains around scalable infrastructure and go-to-market alignment. They will need robust "
                f"solutions to manage their new European operations without slowing down their engineering velocity."
            )
            
        llm = ChatGroq(
            temperature=0.2,
            model_name="llama-3.3-70b-versatile", 
            api_key=settings.GROQ_API_KEY
        )
        
        chain = prompt | llm
        response = chain.invoke({
            "company": company,
            "icp": icp,
            "signals": "\n".join(signals_list)
        })
        
        return response.content
    except Exception as e:
        return f"Error analyzing signals: {str(e)}"

@tool("tool_outreach_automated_sender")
def tool_outreach_automated_sender(email: str, account_brief: str, signals: str) -> str:
    """
    Generates a highly personalized email referencing the signals and account brief,
    and sends it via SMTP or SendGrid.
    
    Args:
        email (str): The target recipient email address.
        account_brief (str): The two-paragraph account brief generated by the research analyst.
        signals (str): JSON string containing the harvested company signals.
        
    Returns:
        str: Status of the sent email along with the generated email content.
    """
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    
    print(f"[Tool] Drafting and sending personalized outreach to {email}...")
    
    try:
        signals_data = json.loads(signals)
        signals_list = signals_data.get("signals", [])
        company = signals_data.get("company", "your company")
    except json.JSONDecodeError:
        signals_list = [signals]
        company = "your company"
        
    # Generate the personalized email using Llama 3
    prompt = PromptTemplate.from_template(
        """You are a top-tier B2B Account Executive. Draft a highly personalized, concise cold email.
        
        CRITICAL CONSTRAINT: You MUST explicitly reference at least one of the specific growth signals 
        (e.g., funding, hiring trends, leadership changes) provided below.
        
        Target Email / Persona: {email}
        Account Context (Brief): {brief}
        Specific Signals to reference:
        {signals}
        
        Draft the email with a compelling subject line. 
        Format as:
        Subject: [Your Subject]
        
        [Email Body]"""
    )
    
    try:
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "mock":
             email_content = (
                 f"Subject: Congrats on the Series B & European Expansion, {company}!\n\n"
                 f"Hi there,\n\n"
                 f"I noticed {company} recently secured a $15M Series B and brought on a new VP of Sales "
                 f"to spearhead your European expansion. With engineering headcount up 20%, scaling your operations "
                 f"smoothly is likely a top priority right now.\n\n"
                 f"Given our focus on the account brief insights, we help rapidly growing teams establish "
                 f"scalable infrastructure. I'd love to share how we can support your next phase of growth.\n\n"
                 f"Open to a quick chat next week?\n\n"
                 f"Best,\nFireReach Team"
             )
        else:
            llm = ChatGroq(
                temperature=0.7,
                model_name="llama-3.3-70b-versatile", 
                api_key=settings.GROQ_API_KEY
            )
            chain = prompt | llm
            response = chain.invoke({
                "email": email,
                "brief": account_brief,
                "signals": "\n".join(signals_list)
            })
            email_content = response.content
            
    except Exception as e:
        email_content = f"Subject: Connection regarding {company}\n\nHi,\n\nI was hoping to connect about your recent growth. (Error generating full text: {str(e)})"
    
    # Attempt to send via SendGrid if key is provided
    delivery_status = "Simulated delivery (no SendGrid API key provided)"
    if settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != "mock":
        try:
            sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            
            # Parse subject and body from LLM output
            lines = email_content.split('\n')
            subject = "Connecting"
            if lines[0].startswith("Subject: "):
                subject = lines[0].replace("Subject: ", "").strip()
                body = "\n".join(lines[1:]).strip()
            else:
                body = email_content
                
            from_email = Email(settings.SENDER_EMAIL)
            to_email = To(email)
            content = Content("text/plain", body)
            mail = Mail(from_email, to_email, subject, content)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            delivery_status = f"Sent successfully via SendGrid (Status: {response.status_code})"
        except Exception as e:
            delivery_status = f"Failed to send email: {str(e)}"
            
    result = {
        "delivery_status": delivery_status,
        "email_content": email_content
    }
    
    return json.dumps(result)
