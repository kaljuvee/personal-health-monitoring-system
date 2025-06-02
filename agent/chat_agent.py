import os
import json
from typing import Dict, List, Tuple, Any
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.tools import tool

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
)

# Define the report reading tool
@tool
def read_health_report(report_path: str) -> Dict:
    """Read and parse a health monitoring report."""
    try:
        with open(report_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to read report: {str(e)}"}

# Define the tools list
tools = [read_health_report]

# Create the tool node
tool_node = ToolNode(tools)

# Define the state type
StateType = Dict[str, Any]

# Define the agent prompt
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful health monitoring assistant that can analyze health reports.
    You have access to health monitoring reports in the reports directory.
    When asked about health data, use the read_health_report tool to access the data.
    Provide clear, concise answers based on the data available."""),
    MessagesPlaceholder(variable_name="messages"),
    MessagesPlaceholder(variable_name="agent_messages"),
])

# Define the agent node
def agent_node(state: StateType) -> StateType:
    """Process the user's message and generate a response."""
    messages = state["messages"]
    agent_messages = state.get("agent_messages", [])
    
    # Generate response using the LLM
    response = llm.invoke(
        agent_prompt.format_messages(
            messages=messages,
            agent_messages=agent_messages
        )
    )
    
    # Update state with the response
    state["agent_messages"] = agent_messages + [response]
    return state

# Create the graph
workflow = StateGraph(StateType)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# Add edges
workflow.add_edge("agent", "tools")
workflow.add_edge("tools", "agent")

# Set entry point
workflow.set_entry_point("agent")

# Compile the graph
app = workflow.compile()

def chat_with_agent(user_message: str) -> str:
    """Process a user message and return the agent's response."""
    try:
        # Initialize state with proper message types
        state = {
            "messages": [
                SystemMessage(content="You are a helpful health monitoring assistant."),
                HumanMessage(content=user_message)
            ],
            "agent_messages": []
        }
        
        # Run the graph
        result = app.invoke(state)
        
        # Debug output
        print("[DEBUG] Result from app.invoke:", result)
        print("[DEBUG] Keys in result:", list(result.keys()))
        if "agent_messages" in result:
            print("[DEBUG] agent_messages:", result["agent_messages"])
        
        # Return the last agent message or a fallback message
        if result.get("agent_messages") and len(result["agent_messages"]) > 0:
            return result["agent_messages"][-1].content
        else:
            return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
            
    except Exception as e:
        print(f"[ERROR] An error occurred: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request: {str(e)}"

if __name__ == "__main__":
    # Example usage
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        response = chat_with_agent(user_input)
        print(f"Assistant: {response}")
