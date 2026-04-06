# src/tools/registry.py

from src.tools.search_tool import SEARCH_TOOL_SPEC, search_travel_data
from src.tools.calculator_tool import CALCULATOR_TOOL_SPEC, calculate_trip_budget
import threading
import logging
import json
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    filename="tool_timeout_logs.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

TOOLS = [
    {
        "spec": SEARCH_TOOL_SPEC,
        "function": search_travel_data
    },
    {
        "spec": CALCULATOR_TOOL_SPEC,
        "function": calculate_trip_budget
    }
]


def get_tool_specs():
    return [tool["spec"] for tool in TOOLS]


def make_tool_runner(func):
    return lambda *args, **kwargs: execute_tool_with_timeout(func, *args, **kwargs)


def get_tool_map():
    return {
        tool["spec"]["name"]: make_tool_runner(tool["function"])
        for tool in TOOLS
    }


def log_timeout_event(tool_name):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "ERROR",
        "data": {
            "error_code": "TIMEOUT",
            "tool_name": tool_name,
            "message": "Tool execution exceeded timeout duration."
        }
    }

    Path("logs").mkdir(exist_ok=True)
    log_file = "logs/tool_execution_logs.jsonl"

    try:
        with open(log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Failed to log timeout event: {e}")


def execute_tool_with_timeout(tool_function, *args, timeout_duration=30, **kwargs):
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = tool_function(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout_duration)

    if thread.is_alive():
        logging.error(f"Timeout occurred for tool: {tool_function.__name__}")
        log_timeout_event(tool_function.__name__)
        raise TimeoutError(f"Tool execution exceeded {timeout_duration} seconds.")

    if exception[0]:
        raise exception[0]

    return result[0]