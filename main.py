import os
import time
import threading
import itertools
import streamlit as st
from graph import Get_workflow as build_graph

# ========== Streamlit UI ==========
st.set_page_config(page_title="AI Proposal Generator", layout="centered")
st.title("📄 AI-Powered Proposal Generator")
st.markdown("Enter your client's request and get a beautifully structured proposal!")

# Input Section
api_key = st.sidebar.text_input("🔑 Google API Key", type="password", placeholder="Enter your Google API key...")
client_name = st.sidebar.text_input("✍️ Client Name", placeholder="Enter the client name...")
client_input = st.text_area("📝 Client Request", placeholder="Enter the client's project requirements here...")

# Proposal Generation Button
if st.button("Generate Proposal"):
    if not api_key.strip():
        st.warning("⚠️ Please enter your Google API key.")
    elif not client_input.strip():
        st.warning("⚠️ Please enter the client's project request.")
    else:
        # Set the API key in the environment for this session
        os.environ["GOOGLE_API_KEY"] = api_key

        # Prepare initial state
        state = {
            "client_name": client_name,
            "UserInput": client_input,
        }

        # Status Messages
        progress_messages = [
            "🔍 Analyzing your client request...",
            "🧠 Identifying project type and category...",
            "📐 Designing project scope...",
            "⏱️ Estimating timeline...",
            "💰 Calculating pricing packages...",
            "📝 Writing a clean and professional proposal...",
            "📦 Finalizing the PDF document..."
        ]

        # Display dynamic status updates
        status_placeholder = st.empty()
        final_state = {}

        # Graph runner function
        def run_graph():
            graph = build_graph()
            result = graph.invoke(state)
            final_state.update(result)

        # Start background thread
        thread = threading.Thread(target=run_graph)
        thread.start()

        # Rotate status messages while graph runs
        for msg in itertools.cycle(progress_messages):
            if not thread.is_alive():
                break
            status_placeholder.info(msg)
            time.sleep(5)

        thread.join()
        status_placeholder.empty()

        # Display results
        if "proposal_pdf" in final_state:
            st.success("✅ Proposal Generated Successfully!")
            st.download_button(
                label="📄 Download Proposal PDF",
                data=final_state["proposal_pdf"],
                file_name=f"{client_name or 'client'}_proposal.pdf",
                mime="application/pdf"
            )
        else:
            st.error("❌ Proposal generation failed.")
            st.stop()

        # Display proposal details (summary)
        st.subheader("📌 Proposal Summary")
        st.markdown(final_state.get("project_scope", "_No scope generated._"))
        st.markdown(f"**🕒 Estimated Duration:** {final_state.get('estimated_timeline', '?')} weeks")
        st.markdown(f"**💵 Budget Estimate:** {final_state.get('pricing', 'N/A')}")
        st.markdown(f"**📣 Justification:** {final_state.get('justification', 'N/A')}")
