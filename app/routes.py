from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.schemas import ProposalRequest, ProposalResponse
from graph import Get_workflow
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
import logging
import os
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate-proposal")
def generate_proposal(payload: ProposalRequest):

    if not payload.api_key.startswith("AIza"):
        raise HTTPException(
            status_code=400,
            detail="Invalid Google API key"
        )

    # TEMPORARY use (not stored)
    os.environ["GOOGLE_API_KEY"] = payload.api_key

    try:
        graph = Get_workflow()
        final_state = graph.invoke({
            "client_name": payload.client_name,
            "UserInput": payload.user_input,
        })

        return {
            "project_scope": final_state.get("project_scope", ""),
            "estimated_timeline": final_state.get("estimated_timeline", 0),
            "pricing": final_state.get("pricing", ""),
            "justification": final_state.get("justification", ""),
            "full_proposal": final_state.get("proposal_markdown", ""),
            "client_name": payload.client_name
        }




    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



@router.post("/download-pdf")
def download_pdf(payload: dict):
    try:
        from weasyprint import HTML
        from markdown import markdown

        client_name = payload.get("client_name", "Valued Client")
        business_name = payload.get("business_name", "")
        proposal_md = payload.get("full_proposal", "")

        proposal_html = markdown(proposal_md)

        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial;
                    margin: 60px;
                    line-height: 1.8;
                }}
                .cover {{
                    text-align: center;
                    margin-top: 200px;
                    page-break-after: always;
                }}
                .cover h1 {{
                    font-size: 42px;
                    margin-bottom: 20px;
                }}
                .cover h2 {{
                    font-size: 28px;
                    color: #555;
                }}
                h1, h2, h3 {{
                    page-break-after: avoid;
                }}
            </style>
        </head>
        <body>

            <!-- COVER PAGE -->
            <div class="cover">
                <h1>Project Proposal</h1>
                <h2>{business_name}</h2>
                <p><strong>Prepared for:</strong> {client_name}</p>
            </div>

            <!-- ACTUAL PROPOSAL -->
            {proposal_html}

        </body>
        </html>
        """

        pdf_bytes = HTML(string=html).write_pdf()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=proposal.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
