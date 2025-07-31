# AI-Powered Proposal Generator

Generate professional, structured business proposals from client requirements using AI and a multi-agent workflow.

## Features

- **Streamlit Web UI**: Simple interface for entering client requests and downloading proposals.
- **Automated Multi-Agent Workflow**: 
  - Extracts project type, requirements, and duration.
  - Classifies use-case and category.
  - Generates detailed technical scope.
  - Estimates timeline and budget.
  - Writes a professional proposal and exports as PDF.
- **PDF Export**: Download a beautifully formatted proposal PDF.

## Project Structure

```
graph.py
main.py
methods.py
requirements.txt
```

- [`main.py`](main.py): Streamlit app entry point.
- [`graph.py`](graph.py): Defines the workflow graph and agent sequence.
- [`methods.py`](methods.py): Implements all agent logic and state management.
- [`requirements.txt`](requirements.txt): Python dependencies.

## Setup

### 1. Clone the Repository

```sh
git clone https://github.com/hassan3208/Proposal-writing-AI-Agent
cd <your-project-folder>
```

### 2. Install Dependencies

It's recommended to use a virtual environment:

```sh
pip install -r requirements.txt
```

### 3. Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

- Download and install `wkhtmltopdf` for your OS.
- Make sure the path in `methods.py` matches your installation:
  - Default: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe` (Windows)
  - Update if installed elsewhere.

### 4. Set Up Google API Key

- Obtain a Google API key for Gemini (Google GenAI).
- Add it to your `.env` file:

```
GOOGLE_API_KEY='your-google-api-key'
```

Or enter it in the Streamlit sidebar at runtime.

## Usage

### Run the Streamlit App

```sh
streamlit run main.py
```

- Enter your Google API key in the sidebar.
- Enter the client name and project requirements.
- Click **Generate Proposal**.
- Download the generated PDF.

## How It Works

1. **InputAgent**: Extracts project type, requirements, and duration from user input.
2. **UseCaseClassifierAgent**: Classifies the project category.
3. **ScopeGeneratorAgent**: Generates a detailed technical scope.
4. **TimelineEstimatorAgent**: Estimates project timeline and provides justification.
5. **BudgetEstimatorAgent**: Suggests pricing tiers.
6. **ProposalWriterAgent**: Writes and formats the proposal, exporting as PDF.

The workflow is defined in [`graph.py`](graph.py) and agent logic in [`methods.py`](methods.py).

## Customization

- Update the PDF template or proposal sections in [`methods.py`](methods.py) as needed.
- Add more agents or modify the workflow in [`graph.py`](graph.py).

## Troubleshooting

- **PDF not generated?**  
  Ensure `wkhtmltopdf` is installed and the path is correct.
- **API errors?**  
  Check your Google API key and network connection.
- **Proposal generation failed?**  
  Review the Streamlit logs for error details.

## License

MIT License

---

**Made with [LangChain](https://python.langchain.com/), [LangGraph](https://github.com/langchain-ai/langgraph),
