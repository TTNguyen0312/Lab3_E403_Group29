# src/tools/search_tool.py

from typing import Dict, Any, List
from src.data.mock import MOCK_TRAVEL_DATA


SEARCH_TOOL_SPEC = {
    "name": "search_travel_data",
    "description": (
        "Search structured travel data for a given city and category. "
        "Use this tool to find attractions, food, hotel, or transport options. "
        "Supports optional filters using fields from the mock data such as district, best_time, "
        "family_friendly, indoor, meal_type, vegetarian_friendly, stars, "
        "breakfast_included, cost_unit, currency, transport_mode, and shared_option. "
        "Input: city (string), category (string), max_results (int, optional), "
        "query (string, optional), plus any optional filter fields. "
        "Returns a JSON object with matching items."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string"},
            "category": {
                "type": "string",
                "enum": ["attractions", "food", "hotel", "transport"]
            },
            "max_results": {"type": "integer", "default": 5},
            "query": {"type": "string"},

            "district": {"type": "string"},
            "best_time": {"type": "string"},
            "family_friendly": {"type": "boolean"},
            "indoor": {"type": "boolean"},
            "meal_type": {"type": "string"},
            "vegetarian_friendly": {"type": "boolean"},
            "stars": {"type": "integer"},
            "breakfast_included": {"type": "boolean"},

            "cost_unit": {"type": "string"},
            "currency": {"type": "string"},

            "transport_mode": {"type": "string"},
            "shared_option": {"type": "boolean"}
        },
        "required": ["city", "category"],
        "additionalProperties": True
    }
}

def _normalize_text(value: Any) -> str:
    return "" if value is None else str(value).strip().lower()


def _matches_query(item: Dict[str, Any], query: str) -> bool:
    if not query:
        return True

    q = _normalize_text(query)
    haystack = " ".join(
        _normalize_text(item.get(field))
        for field in [
            "id", "name", "type", "city", "district",
            "description", "notes", "best_time",
            "meal_type", "cost_unit", "transport_mode"
        ]
    )
    return q in haystack


def _matches_filters(item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    for key, expected in filters.items():
        if expected is None or expected == "":
            continue
        if key not in item:
            continue

        actual = item.get(key)

        if isinstance(expected, str):
            if _normalize_text(actual) != _normalize_text(expected):
                return False
        else:
            if actual != expected:
                return False

    return True


def search_travel_data(
    city: str,
    category: str,
    max_results: int = 5,
    query: str = "",
    **filters: Any
) -> Dict[str, Any]:
    city_key = _normalize_text(city)
    category_key = _normalize_text(category)

    # Defensive fix for common wrong filter usage
    if _normalize_text(filters.get("cost_unit")) in {"vnd", "usd"} and "currency" not in filters:
        filters["currency"] = filters["cost_unit"]
        del filters["cost_unit"]

    aliases = {
        "attraction": "attractions",
        "attractions": "attractions",
        "food": "food",
        "foods": "food",
        "hotel": "hotel",
        "hotels": "hotel",
        "transport": "transport",
        "transports": "transport",
    }
    category_key = aliases.get(category_key, category_key)

    city_data = MOCK_TRAVEL_DATA.get(city_key, {})
    items: List[Dict[str, Any]] = city_data.get(category_key, [])

    matched = [
        item for item in items
        if _matches_query(item, query) and _matches_filters(item, filters)
    ]

    results = matched[:max_results]

    return {
        "city": city,
        "category": category_key,
        "count": len(results),
        "filters": filters,
        "results": results
    }