import os
import json


def classify_record(record):
    """
    Map a log record to one of:
      - JSON Parser Error
      - Hallucination Error
      - Timeout
      - None
    """
    event = record.get("event", "")
    data = record.get("data", {})

    # Preferred schema: ERROR + error_code
    if event == "ERROR":
        code = data.get("error_code", "")
        if code == "JSON_PARSER_ERROR":
            return "JSON Parser Error"
        if code == "HALLUCINATION_ERROR":
            return "Hallucination Error"
        if code == "TIMEOUT":
            return "Timeout"

    # Fallback schema: TOOL_ERROR message matching
    if event == "TOOL_ERROR":
        msg = str(data.get("error", "")).lower()

        if "unexpected keyword argument" in msg:
            return None  # tool/runtime bug, not one of the 3 required categories

        if "hallucinated tool" in msg or "unknown tool" in msg:
            return "Hallucination Error"

        if "timeout" in msg:
            return "Timeout"

    return None


def parse_json_lines_file(file_path):
    """
    Parse a file containing one JSON object per line.
    Returns a list of parsed records.
    """
    records = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # skip malformed line
                continue
    return records


def parse_logs(log_dir):
    error_counts = {
        "JSON Parser Error": 0,
        "Hallucination Error": 0,
        "Timeout": 0
    }
    total_runs = 0

    for file_name in os.listdir(log_dir):
        if not (file_name.endswith(".json") or file_name.endswith(".jsonl")):
            continue

        file_path = os.path.join(log_dir, file_name)
        records = parse_json_lines_file(file_path)

        if not records:
            continue

        total_runs += 1

        run_errors = set()
        has_final_answer = False

        for record in records:
            event = record.get("event", "")
            if event == "FINAL_ANSWER":
                has_final_answer = True

            err = classify_record(record)
            if err:
                run_errors.add(err)

        for err in run_errors:
            error_counts[err] += 1

    successful_runs = total_runs - sum(error_counts.values())
    aggregate_reliability = (successful_runs / total_runs) * 100 if total_runs > 0 else 0

    print("Error Counts:")
    for error, count in error_counts.items():
        print(f"  {error}: {count}")
    print(f"\nAggregate Reliability: {aggregate_reliability:.2f}%")


if __name__ == "__main__":
    log_directory = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "logs")
    )
    parse_logs(log_directory)