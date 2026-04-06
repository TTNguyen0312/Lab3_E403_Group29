import os
import re
from typing import TypedDict, List, Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from src.core.openai_provider import OpenAIProvider
from src.tools.sample_tool import sample_tool_function
from src.tools.find_destinations import find_destinations
from src.prompt.system_prompt import SYSTEM_PROMPT_TEMPLATE
from src.telemetry.logger import logger

load_dotenv()

# ======================
# 🔹 STATE DEFINITION
# ======================
class AgentState(TypedDict):
    input: str
    messages: List[str]
    last_response: str
    tool_name: str
    tool_args: str
    observation: str
    used_tools: List[str]
    steps: int


# ======================
# 🔹 INIT
# ======================
model_name = os.getenv("DEFAULT_MODEL", "gpt-4o")
api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAIProvider(model_name=model_name, api_key=api_key)

tools = {
    "find_destination": find_destinations,
    "estimate_cost": lambda args: f"Estimated cost for {args}",
    "sample_tool": sample_tool_function
}


def get_system_prompt():
    tool_descriptions = "\n".join([
        "- find_destination: Suggest travel destinations based on user preferences.",
        "- estimate_cost: Estimate trip costs based on destination and duration.",
        "- sample_tool: A sample tool for testing."
    ])
    return SYSTEM_PROMPT_TEMPLATE.format(tool_descriptions=tool_descriptions)


# ======================
# 🔹 NODE 1: LLM
# ======================
def llm_node(state: AgentState) -> AgentState:
    prompt = state["input"] + "\n".join(state["messages"])

    result = llm.generate(prompt, system_prompt=get_system_prompt())
    response_text = result["content"]

    logger.log_event("LLM_RESPONSE", {"response": response_text})

    state["last_response"] = response_text
    state["messages"].append(response_text)
    state["steps"] += 1

    return state


# ======================
# 🔹 NODE 2: PARSE ACTION
# ======================
def parse_node(state: AgentState) -> AgentState:
    text = state["last_response"]

    action_match = re.search(r"Action:\s*(\w+)\s*\((.*?)\)", text, re.DOTALL)

    if action_match:
        state["tool_name"] = action_match.group(1)
        state["tool_args"] = action_match.group(2)
    else:
        state["tool_name"] = ""
        state["tool_args"] = ""

    return state


# ======================
# 🔹 NODE 3: TOOL EXECUTION
# ======================
def tool_node(state: AgentState) -> AgentState:
    tool_name = state["tool_name"]
    args = state["tool_args"]

    if tool_name in tools:
        try:
            result = tools[tool_name](args)
            state["observation"] = str(result)
            state["used_tools"].append(tool_name)

            logger.log_event("TOOL_CALL", {
                "tool": tool_name,
                "args": args
            })

        except Exception as e:
            state["observation"] = f"Error: {str(e)}"
    else:
        state["observation"] = f"Tool {tool_name} not found"

    # append observation back
    state["messages"].append(f"Observation: {state['observation']}")

    return state


# ======================
# 🔹 ROUTER (DECISION)
# ======================
def should_continue(state: AgentState) -> str:
    text = state["last_response"]

    # Final Answer → END
    if "Final Answer:" in text:
        return "end"

    # If action exists → go tool
    if state["tool_name"]:
        return "tool"

    # Otherwise → LLM again
    return "llm"


# ======================
# 🔹 GRAPH BUILD
# ======================
graph = StateGraph(AgentState)

graph.add_node("llm", llm_node)
graph.add_node("parse", parse_node)
graph.add_node("tool", tool_node)

graph.set_entry_point("llm")

# Flow
graph.add_edge("llm", "parse")

graph.add_conditional_edges(
    "parse",
    should_continue,
    {
        "tool": "tool",
        "llm": "llm",
        "end": END
    }
)

graph.add_edge("tool", "llm")

app = graph.compile()


# ======================
# 🔹 RUN
# ======================
if __name__ == "__main__":
    print("LangGraph Travel Agent Ready!")

    while True:
        user_input = input(">> ")
        if user_input.lower() == "exit":
            break

        state = {
            "input": user_input,
            "messages": [],
            "last_response": "",
            "tool_name": "",
            "tool_args": "",
            "observation": "",
            "used_tools": [],
            "steps": 0
        }

        result = app.invoke(state)

        final_text = result["last_response"]

        print("\n=== FINAL OUTPUT ===")
        print(final_text)
        print("\nUsed tools:", result["used_tools"])