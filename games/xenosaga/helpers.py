from __future__ import annotations

import json
import sqlite3
from typing import Any

import pandas as pd
from dash import html
from pandas.api.types import is_numeric_dtype


def load_episode_rows(connection: sqlite3.Connection, table_name: str) -> pd.DataFrame:
    """Load, normalize, and sort enemy rows for a single episode table."""
    frame = pd.read_sql_query(f'SELECT * FROM "{table_name}"', connection)
    if "uuid" in frame.columns:
        frame = frame.drop(columns=["uuid"])
    frame = frame.sort_values(by=["Name"], na_position="last")
    return frame


def build_column_defs(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Build ag-grid column definitions with numeric-aware filtering/formatting."""
    # Determine if a column is numeric using dtype first, then sampled values
    def is_numeric_col(column_name: str) -> bool:
        if is_numeric_dtype(frame[column_name].dtype):
            return True

        non_na_values = frame[column_name].dropna()
        if non_na_values.empty:
            return False

        sample_values = non_na_values.sample(min(100, len(non_na_values)), random_state=0).tolist()
        try:
            for value in sample_values:
                first_part = str(value).split("-")[0].strip().replace(",", "")
                float(first_part)
            return True
        except (TypeError, ValueError):
            return False

    column_defs: list[dict[str, Any]] = []
    for field in frame.columns:
        numeric_col = is_numeric_col(field)
        col_def: dict[str, Any] = {
            "field": field,
            "filter": "agNumberColumnFilter" if numeric_col else "agTextColumnFilter",
        }
        if numeric_col:
            field_name = json.dumps(field)
            col_def["valueGetter"] = {"function": f"extractRangeStart(params, {field_name})"}
            col_def["valueFormatter"] = {"function": "formatNumberWithCommas(params)"}
        if field == "Name":
            col_def["pinned"] = "left"
        column_defs.append(col_def)
    return column_defs


def format_value(value: Any) -> str:
    """Format values for display, returning comma-separated numbers or N/A."""
    if value is None:
        return "N/A"
    if isinstance(value, str) and value == "":
        return "N/A"
    if not isinstance(value, str) and pd.isna(value):
        return "N/A"
    try:
        numeric_value = float(value)
        if numeric_value.is_integer():
            return f"{int(numeric_value):,}"
        return f"{numeric_value:,}"
    except (ValueError, TypeError):
        return str(value)


def apply_element_style(text: str) -> list[Any]:
    """Apply color styling to known elemental/status tokens in comma-separated text."""
    color_styles: dict[str, str] = {
        "Lightning": "yellow",
        "Fire": "red",
        "Ice": "lightblue",
        "Yes": "green",
        "No": "red",
        "Cannot": "red",
    }
    parts: list[str] = text.split(", ")
    spans: list[Any] = []
    for i, part in enumerate(parts):
        color = color_styles.get(part)
        if color:
            spans.append(html.Span(part, style={"color": color}))
        else:
            spans.append(html.Span(part))
        if i < len(parts) - 1:
            spans.append(", ")
    return spans
