# Proposal Writing AI Agent

An AI-powered proposal generation system that automates professional proposal writing using structured workflows and Large Language Models (LLMs).

This project is built as a **modular, API-driven AI agent** designed for freelancers, agencies, and service providers.

---

## Features

- AI-driven proposal generation
- Modular agent-based architecture
- FastAPI backend
- Clean separation of backend and frontend
- Extensible workflow design (LangGraph-ready)
- Simple frontend UI

---

<img width="2879" height="1519" alt="image" src="https://github.com/user-attachments/assets/52e59a36-d95b-4fb8-a857-0ba54c255802" />


## Project Structure

```text
Proposal_Agent/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI entry point
│   ├── routes.py     # API routes
│   └── schemas.py    # Request & response models
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── graph.py          # AI workflow / agent graph
├── methods.py        # Core AI logic & helpers
├── requirements.txt  # Python dependencies
````

---

## Tech Stack

* **Backend:** Python, FastAPI
* **AI / LLMs:** OpenAI / Gemini
* **Agent Workflow:** LangGraph-style orchestration
* **Frontend:** HTML, CSS, JavaScript
* **API:** REST (JSON)

---

## Installation


## Environment Variables

Create a `.env` file in the root directory:

```env
GEMINAI_API_KEY=your_api_key_here
```

> Do not commit `.env` to GitHub.

---

## Run the Application

```bash
uvicorn app.main:app --reload
```

* API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Frontend: Open `frontend/index.html`

---

## API Example

**POST** `/api/generate-proposal`

```json
{
  "client_name": "ABC Company",
  "project_description": "AI-powered proposal system",
  "budget": "$3000",
  "timeline": "3 weeks"
}
```

---

## Author

**Hassan Imran**  
AI / ML Developer  
Like and follow this repo 💖
