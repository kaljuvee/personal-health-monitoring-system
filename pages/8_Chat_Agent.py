import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from agent.chat_agent import chat_with_agent

st.set_page_config(
    page_title="Health Chat Agent",
    page_icon="💬",
    layout="wide"
)

st.title("Health Monitoring Chat Assistant 🤖")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Sample questions
sample_questions = [
    "What is the average heart rate in the latest report?",
    "Is the blood glucose level normal?",
    "What is the risk score trend?",
    "Are there any health alerts?",
    "Show me the latest health metrics",
    "What is the highest heart rate recorded?",
    "Is there any concerning trend in the data?"
]

# Create columns for the sample questions
col1, col2 = st.columns(2)
with col1:
    st.subheader("Sample Questions")
    for i, question in enumerate(sample_questions[:4]):
        if st.button(question, key=f"q1_{i}"):
            st.session_state.messages.append({"role": "user", "content": question})
            response = chat_with_agent(question)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

with col2:
    st.subheader("More Questions")
    for i, question in enumerate(sample_questions[4:]):
        if st.button(question, key=f"q2_{i}"):
            st.session_state.messages.append({"role": "user", "content": question})
            response = chat_with_agent(question)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Chat input
if prompt := st.chat_input("Ask about your health data"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        response = chat_with_agent(prompt)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Add a clear chat button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Add some helpful information
with st.expander("ℹ️ About this Chat Agent"):
    st.markdown("""
    This chat agent can help you analyze your health monitoring data. You can:
    - Ask about specific metrics (heart rate, blood glucose, risk scores)
    - Get trend analysis
    - Check for health alerts
    - Compare different time periods
    
    The agent uses AI to understand your questions and provide relevant insights from your health reports.
    """)
