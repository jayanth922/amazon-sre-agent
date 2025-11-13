#!/usr/bin/env python3
"""
Simple Streamlit UI for SRE Agent

Run with: streamlit run ui/streamlit_app.py
"""

import asyncio
import os
import sys
from pathlib import Path

import streamlit as st

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sre_agent.agent_runtime import invoke_sre_agent_async


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "provider" not in st.session_state:
        st.session_state.provider = "groq"


async def get_agent_response(prompt: str, provider: str) -> str:
    """Get response from SRE agent."""
    return await invoke_sre_agent_async(prompt, provider)


def main():
    st.set_page_config(
        page_title="SRE Agent Chat",
        page_icon="🤖",
        layout="wide",
    )

    init_session_state()

    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")

        provider = st.selectbox(
            "LLM Provider",
            options=["groq", "anthropic"],
            index=0 if st.session_state.provider == "groq" else 1,
            help="Select the LLM provider to use",
        )
        st.session_state.provider = provider

        st.divider()

        st.markdown("### 📊 Agent Info")
        st.markdown("""
        **Specialized Agents:**
        - 🏗️ Kubernetes Infrastructure
        - 📋 Application Logs
        - 📈 Performance Metrics
        - 📚 Operational Runbooks
        """)

        st.divider()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        st.markdown("### 💡 Example Queries")
        st.markdown("""
        - "What are Kubernetes pod security best practices?"
        - "How do I troubleshoot crash looping pods?"
        - "Explain application monitoring strategies"
        - "What's in the incident response playbook?"
        """)

    # Main chat interface
    st.title("🤖 SRE Agent Chat")
    st.markdown("Ask questions about Kubernetes, logs, metrics, and operations!")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about SRE operations..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    response = asyncio.run(
                        get_agent_response(prompt, st.session_state.provider)
                    )
                    st.markdown(response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )


if __name__ == "__main__":
    # Check for API keys
    if not os.getenv("GROQ_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        st.error(
            "⚠️ No API keys found! Please set GROQ_API_KEY or ANTHROPIC_API_KEY in sre_agent/.env"
        )
        st.stop()

    main()
