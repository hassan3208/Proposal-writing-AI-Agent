from typing import Annotated
from typing_extensions import TypedDict
import os
import json
import re
from markdown import markdown
import pdfkit
from jinja2 import Template
from pydantic import BaseModel, Field
from typing import Literal
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import io






class WorkingState(TypedDict):
    client_name: str = Field(
        default=''
    )
    
    
    UserInput: str = Field(
        default="")
    
    project_type: Annotated[str,
        Field(
            default=None,
            description="The project is either a website or a mobile app.",
            examples=['Web App', 'Mobile App']
        )
    ]
    
    requirements: Annotated[
        str,
        Field(
            default=None,
            description="The requirements for the project.",
            examples=["User authentication", "Data storage", "Responsive design"]
        )
    ]
    
    duration: Annotated[
        int,
        Field(
            default=None,
            description="The estimated duration for the project in weeks.",
            examples=[2, 4, 6]
        )
    ]
    
    category: str = Field(
        default=None,
        description="The category of the project, such as 'E-commerce', 'Social Media', etc.",
        examples=["E-commerce", "Social Media", "Blog"]
    )
    
    project_scope: str = Field(
        default=None,
        description="The scope of the project, detailing the features and functionalities.",
        examples=["User registration, product listing, shopping cart, payment gateway"]) 
    
    estimated_timeline: int = Field(
        default=None)
    
    justification: str = Field(
        default=None,
        description="The justification for the project, explaining why it is needed.",
        examples=["To improve customer engagement", "To increase sales", "To provide better user experience"]
    )
    
    pricing: str = Field(
        default=None,
        description="The basic package cost for the project in USD and its all features.",
    )
    
    
    proposal_pdf: bytes = Field(
        default=None,
        description="The generated proposal PDF in bytes format."
    )
    
    
def get_structured_input(state: WorkingState) -> str:
    return f"""
    User Input: {state.get('UserInput', 'N/A')}
    project_type: {state.get('project_type', 'N/A')}
    requirements: {state.get('requirements', 'N/A')}
    duration: {state.get('duration', 'N/A')} weeks
    category: {state.get('category', 'N/A')}
    project_scope: {state.get('project_scope', 'Not yet generated')}
    """  
    
    
def InputAgent(state: WorkingState):
    print('Input Agent to gather project details.')
        
    """
    Input Agent to gather project details.
    """
    
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    
    response = model.invoke(f'''
    Generate the output of following input in the given json format:
    Input: {state['UserInput']}
    Output: (
        project_type: Literal['Web App', 'Mobile App'] = Field(description="The project is either a website or a mobile app.",examples=['Web App', 'Mobile App'])
        requirements: str = Field(description="The requirements for the project.", examples=["User authentication", "Data storage", "Responsive design"])
        duration: int = Field(description="The estimated duration for the project in weeks.", examples=[2, 4, 6])
    )    
    ''')
    
    response = response.content
    # Only keep the JSON content from the response
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        response_json = match.group(0)
        response_json = json.loads(response_json)
        
        state["project_type"]=response_json['project_type']
        state["requirements"]=response_json['requirements']
        state["duration"]=response_json['duration']
        
    else:
        print("No JSON object found in response.")
    
    return state
    


def UseCaseClassifierAgent(state: WorkingState):
    print("Use Case Classifier Agent to identify project category.")
    
    """
    Use Case Agent to generate use cases based on project details.
    Task: Identify project category
    """
    
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    
    response = model.invoke(f'''
    Generate the output of following input in the given json format:
    Input: {state['UserInput']}
    Output: category: (Web Application/mobile app) – (Online Store etc)
    ''')
    
    response = response.content
    # Only keep the JSON content from the response
    import re
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        response_json = match.group(0)
        response_json = json.loads(response_json)
        state["category"] = response_json['category']
    else:
        print("No JSON object found in response.")
    
    return state



def ScopeGeneratorAgent(state: WorkingState):
    print("Scope Generation Agent to create a project scope based on use cases.")
    
    """
    Scope Generation Agent to create a project scope based on use cases.
    """
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    
    response = model.invoke(f"""You are a software architect. Based on the following client project details, generate a detailed technical scope:

    Client Project Details:
    \"\"\"{get_structured_input(state)}\"\"\"
    
    Include:
    - Features list
    - Tech stack suggestions (Frontend + Backend + DB)
    - APIs or 3rd-party tools (if needed)
    
    Respond in bullet points.
    """
    )
    
    state["project_scope"] = response.content
     
    
    
    return state



def TimelineEstimatorAgent(state: WorkingState):
    print("Timeline Estimation Agent to estimate the project timeline based on scope.")
    
    """
    Timeline Estimation Agent to estimate the project timeline based on scope.
    """
    
    
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    
    response = model.invoke(f"""You are a project manager. Estimate a realistic timeline for this project based on the scope:

    Project Scope:
    \"\"\"{state['project_scope']}\"\"\"
    
    Output(json):
    (
        estimated_timeline: [weeks]
        justification: [Short explanation]
    )
    """
    
    )
    
    response = response.content
   
    
    
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        response_json = match.group(0)
        response_json = json.loads(response_json)
        state['estimated_timeline'] = response_json['estimated_timeline']
        state['justification'] = response_json['justification']
    else:
        print("No JSON object found in response.")
    
    return state
    


def BudgetEstimatorAgent(state: WorkingState):
    print("Budget Estimation Agent to estimate the project budget based on scope and timeline.")
    
    """
    Budget Estimation Agent to estimate the project budget based on scope and timeline.
    """
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    
    response = model.invoke(f"""You are a freelance pricing strategist. Based on the following project scope and timeline, estimate 3 pricing tiers:

    Scope:
    \"\"\"{state['project_scope']}\"\"\"
    Timeline: {state['estimated_timeline']} weeks
    
    Output(string):
    - Basic Package: [features] – $X
    - Standard Package: [features] – $Y
    - Premium Package: [features] – $Z
    
    Respond with pricing breakdown.
    """    
    )
    
    response = response.content
    
    state['pricing'] = response   

    
    return state



def ProposalWriterAgent(state: WorkingState):
    print("Proposal Writer Agent to create a project proposal based on budget and timeline.")
    
    """
    Proposal Writer Agent to create a project proposal based on budget and timeline.
    """
    
    if not os.environ.get("GOOGLE_API_KEY"):
        raise EnvironmentError("GOOGLE_API_KEY environment variable is not set.")
    
    model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
    
    response = model.invoke(f"""You are a professional business proposal writer.

    Write a detailed proposal based on:
    - Client Name: {state['client_name']}
    - Use-case: {state['project_type']}
    - Scope: {state['project_scope']}
    - Timeline: {state['estimated_timeline']} weeks
    - Budget: {state['pricing']}
    
    Include these sections:
    1. Executive Summary
    2. Project Scope
    3. Technology Stack
    4. Estimated Timeline
    5. Pricing Packages
    6. Why Choose Us
    7. Terms and Conditions
    
    Respond in Markdown format for easy PDF export.
    """
        
    )
    
    markdown_text = response.content
    
    html_body = markdown(markdown_text)

    # HTML Template with styling
    html_template = Template("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {
                font-family: 'Arial', sans-serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #333;
                margin: 40px;
            }
            h1, h2, h3 {
                color: #2C3E50;
                margin-top: 30px;
            }
            ul, ol {
                margin-left: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            table, th, td {
                border: 1px solid #aaa;
                padding: 8px;
            }
            .page-break {
                page-break-after: always;
            }
        </style>
    </head>
    <body>
        {{ body }}
    </body>
    </html>
    """)

    final_html = html_template.render(body=html_body)

    # Save path to wkhtmltopdf
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    
    pdf_bytes = pdfkit.from_string(final_html, False, configuration=config)
    pdf_buffer = io.BytesIO(pdf_bytes)

    # Return PDF binary to Streamlit app
    state["proposal_pdf"] = pdf_buffer.getvalue()
    return state 
    


 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
