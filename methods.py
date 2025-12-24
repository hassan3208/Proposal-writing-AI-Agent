from typing_extensions import TypedDict, NotRequired
import os
import json
import re
from markdown import markdown
from jinja2 import Template
from langchain.chat_models import init_chat_model
from weasyprint import HTML

# =====================================================
# STATE
# =====================================================

class WorkingState(TypedDict):
    client_name: str
    UserInput: str

    project_type: NotRequired[str]
    requirements: NotRequired[str]
    duration: NotRequired[int]
    category: NotRequired[str]
    project_scope: NotRequired[str]

    estimated_timeline: NotRequired[int]
    justification: NotRequired[str]
    pricing: NotRequired[str]

    proposal_markdown: NotRequired[str]   # ✅ ADD THIS
    proposal_pdf: NotRequired[bytes]



# =====================================================
# 1️⃣ UNIFIED ANALYSIS AGENT
# (Input + Category + Scope → ONE LLM CALL)
# =====================================================

def UnifiedAnalysisAgent(state: WorkingState):


    state.setdefault("project_scope", "")
    state.setdefault("project_type", "Custom Project")
    state.setdefault("requirements", state["UserInput"])


    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY not set")

    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

    try:
        response = model.invoke(f"""
        From the client input below, return ONLY valid JSON:

        {{
          "project_type": "Web App or Mobile App",
          "requirements": "key requirements",
          "duration": 6,
          "category": "E-commerce / Service / Blog",
          "project_scope": "detailed technical scope with features and tech stack"
        }}

        Client Input:
        {state['UserInput']}
        """)
        
        # Clean up response content
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Try to find JSON object
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            content = match.group()

        data = json.loads(content)
        state.update(data)
        
        # Validate critical fields
        if "project_scope" not in state:
            state["project_scope"] = f"Project scope for {state.get('project_type', 'custom project')} based on requirements: {state.get('requirements', state['UserInput'][:100])}"
            
    except Exception as e:
        # Fallback if AI fails
        print(f"UnifiedAnalysisAgent Error: {str(e)}")
        state["project_type"] = "Custom Development"
        state["requirements"] = state["UserInput"]
        state["duration"] = 4
        state["category"] = "Custom"
        state["project_scope"] = f"Development of custom solution based on: {state['UserInput']}"

    return state


# =====================================================
# 2️⃣ TIMELINE + BUDGET AGENT
# =====================================================

def TimelineBudgetAgent(state: WorkingState):
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

    # Ensure project_scope exists
    scope = state.get("project_scope") or "Standard development scope"

    try:
        response = model.invoke(f"""
        Based on the project scope below, return ONLY valid JSON:

        {{
          "estimated_timeline": 8,
          "justification": "short explanation",
          "pricing": "3 pricing tiers with features and USD cost"
        }}

        Project Scope:
        {scope}
        """)

        # Clean, parse and update similar to above
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            content = match.group()
            
        data = json.loads(content)
        state.update(data)

        # ✅ NORMALIZE PRICING (OBJECT → STRING)
        pricing = state.get("pricing")

        # Case 1: pricing is a list of objects
        if isinstance(pricing, list):
            lines = []
            for item in pricing:
                if isinstance(item, dict):
                    for k, v in item.items():
                        lines.append(f"{k}: {v}")
                else:
                    lines.append(str(item))
            state["pricing"] = "\n".join(lines)
        
        # Case 2: pricing is a single object
        elif isinstance(pricing, dict):
            lines = []
            for tier, value in pricing.items():
                lines.append(f"{tier}: {value}")
            state["pricing"] = "\n".join(lines)
        
        # Case 3: pricing missing
        elif pricing is None:
            state["pricing"] = "Pricing will be finalized after discussion."


        
    except Exception as e:
        print(f"TimelineBudgetAgent Error: {str(e)}")
        state["estimated_timeline"] = 4
        state["justification"] = "Standard estimation based on requirements"
        state["pricing"] = "Standard Tier: $1000, Premium Tier: $2000"

    return state


# =====================================================
# 3️⃣ PROPOSAL WRITER + PDF (DEPLOYMENT SAFE)
# =====================================================

def ProposalWriterAgent(state: WorkingState):
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

    response = model.invoke(f"""
    You are a senior business consultant and proposal writer.
    
    Your task is to write a **LONG, DETAILED, PROFESSIONAL PROJECT PROPOSAL**
    that would normally span **7–8 pages when converted to PDF**.
    
    IMPORTANT RULES:
    - Write in FULL detail (no short summaries)
    - Each section must have multiple paragraphs
    - Use bullet lists where appropriate
    - Explain the WHY, WHAT, and HOW clearly
    - Assume this proposal will be sent to a serious client
    - Do NOT shorten content to save space
    
    Client Information:
    - Client Name: {state.get('client_name', 'Valued Client')}
    - Project Type: {state.get('project_type')}
    - Category: {state.get('category')}
    - Project Scope: {state.get('project_scope')}
    - Estimated Timeline: {state.get('estimated_timeline')} weeks
    - Pricing: {state.get('pricing')}
    
    STRUCTURE (MANDATORY):
    
    # 1. Executive Summary
    Explain the business problem, client goals, and how this solution helps.
    Minimum: 3–4 paragraphs.
    
    # 2. Company Overview
    Describe our company, experience, expertise, and working philosophy.
    Minimum: 2–3 paragraphs.
    
    # 3. Understanding of Client Requirements
    Rewrite and expand the client requirements in professional language.
    Explain assumptions and expectations.
    
    # 4. Detailed Project Scope
    Break down the scope into modules, features, and phases.
    Explain each feature in detail.
    
    # 5. Technology Stack
    Explain frontend, backend, database, hosting, security, and scalability.
    Justify why each technology is chosen.
    
    # 6. Project Timeline & Milestones
    Explain the timeline week-by-week or phase-by-phase.
    Add deliverables for each phase.
    
    # 7. Pricing & Payment Structure
    Explain pricing tiers, what is included, exclusions, and value justification.
    
    # 8. Quality Assurance & Testing
    Explain testing strategy, QA process, and quality standards.
    
    # 9. Communication & Project Management
    Explain how progress will be shared, meetings, reporting, and tools.
    
    # 10. Risks & Mitigation Strategy
    Explain possible risks and how they will be handled.
    
    # 11. Why Choose Us
    Explain competitive advantages, reliability, and value proposition.
    
    # 12. Terms & Conditions
    Include assumptions, ownership, confidentiality, and support terms.
    
    FINAL RULE:
    This proposal must be **long enough that when converted to PDF,
    it spans approximately 7–8 pages**.
    
    Respond ONLY in Markdown.
    """)

    state["proposal_markdown"] = response.content


    # Markdown → HTML
    html_body = markdown(response.content)

    html_template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
                color: #333;
            }
            h1, h2, h3 {
                color: #2C3E50;
                margin-top: 30px;
            }
            ul {
                margin-left: 20px;
            }
        </style>
    </head>
    <body>
        {{ body }}
    </body>
    </html>
    """)

    final_html = html_template.render(body=html_body)

    # ✅ CLOUD SAFE PDF (NO LOCAL BINARIES)
    pdf_bytes = HTML(string=final_html).write_pdf()
    state["proposal_pdf"] = pdf_bytes

    return state
