from __future__ import annotations
from games.expedition33.helpers import clean_frame, format_value
from pathlib import Path
from typing import Any, TypeAlias, TypedDict
import pandas as pd
import re

CalculatorRow: TypeAlias = dict[str, Any]
CalculatorState: TypeAlias = dict[str, Any]
ComponentChildren: TypeAlias = list[Any]
SkillOption: TypeAlias = dict[str, str]
StyleRule: TypeAlias = dict[str, str]
CharacterStyles: TypeAlias = dict[str, StyleRule]
NumericInput: TypeAlias = int | float | None
ToggleInput: TypeAlias = bool | None
ControlStyles: TypeAlias = dict[str, StyleRule]


class CalculationResult(TypedDict):
    """Normalized payload describing the selected damage scenario."""

    multiplier: float | None
    scenario: str
    source: str
    warning: str | None


class SheetScenario(TypedDict):
    """A spreadsheet breakpoint displayed in the summary table."""

    label: str
    value: float


class CalculatorPayload(TypedDict):
    """Loaded calculator data for a single character."""

    default_attack: float
    records: list[CalculatorRow]
    skills: dict[str, CalculatorRow]


CSV_DIR = Path(__file__).resolve().parents[2] / "assets" / "expedition33" / "clair_skill_damage"

CHARACTER_META = {
    "gustave": {"label": "Gustave"},
    "lune": {"label": "Lune"},
    "maelle": {"label": "Maelle"},
    "monoco": {"label": "Monoco"},
    "sciel": {"label": "Sciel"},
    "verso": {"label": "Verso"},
}

DEFAULT_CHARACTER = "lune"
DEFAULT_SKILLS = {
    "gustave": "Overcharge 0 Charges",
    "lune": "Lightning Dance",
    "maelle": "Burning Canvas",
    "monoco": "Sakapate Estoc",
    "sciel": "End Slice",
    "verso": "Strike Storm",
}
RANK_ORDER = {"D": 0, "C": 1, "B": 2, "A": 3, "S": 4}
VISIBLE_STYLE: StyleRule = {}
HIDDEN_STYLE: StyleRule = {"display": "none"}


def compact(children: ComponentChildren) -> ComponentChildren:
    """Remove placeholder entries from a component list."""

    return [child for child in children if child is not None]


def clean_text(value: Any) -> str:
    """Convert raw CSV values into trimmed display-safe strings."""

    if value is None:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def parse_number(value: Any) -> float | None:
    """Parse a numeric cell value while tolerating sheet punctuation."""

    if value is None:
        return None
    if isinstance(value, (int, float)) and not pd.isna(value):
        return float(value)

    text = clean_text(value).replace(",", "").replace("?", "")
    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def extract_first_int(value: Any) -> int | None:
    """Extract the first integer embedded in a condition string."""

    match = re.search(r"(\d+)", clean_text(value))
    return int(match.group(1)) if match else None


def number_from_row(row: CalculatorRow, *keys: str) -> float | None:
    """Return the first parseable numeric value from the provided columns."""

    for key in keys:
        number = parse_number(row.get(key))
        if number is not None:
            return number
    return None


def text_from_row(row: CalculatorRow, *keys: str) -> str:
    """Return the first non-empty text value from the provided columns."""

    for key in keys:
        text = clean_text(row.get(key))
        if text:
            return text
    return ""


def clamp_int(value: Any, minimum: int, maximum: int) -> int:
    """Clamp user input to an integer range used by calculator controls."""

    try:
        number = int(value)
    except (TypeError, ValueError):
        return minimum
    return max(minimum, min(number, maximum))


def format_multiplier(value: float | None) -> str:
    """Format a damage multiplier for result-card display."""

    if value is None:
        return "-"
    text = f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{text}x"


def calculate_damage(attack: float | None, multiplier: float | None) -> float | None:
    """Convert attack and multiplier values into estimated damage."""

    if attack is None or multiplier is None:
        return None
    return round(attack * multiplier, 2)


def result(
    multiplier: float | None,
    scenario: str,
    source: str,
    warning: str | None = None,
) -> CalculationResult:
    """Build a normalized result payload for a calculated scenario."""

    return {
        "multiplier": multiplier,
        "scenario": scenario,
        "source": source,
        "warning": warning,
    }


def base_result(
    row: CalculatorRow,
    scenario: str | None = None,
    source: str = "Damage Multi",
) -> CalculationResult:
    """Build the default result payload for a skill row."""

    condition = text_from_row(row, "Condition 1", "Condition")
    return result(
        number_from_row(row, "Damage Multi"),
        scenario or ("Base value" if not condition else f"Base value | breakpoint: {condition}"),
        source,
    )


def load_calculator_data() -> dict[str, CalculatorPayload]:
    """Load and normalize every character CSV into calculator-friendly payloads."""

    payloads: dict[str, CalculatorPayload] = {}

    for character in CHARACTER_META:
        frame = clean_frame(pd.read_csv(CSV_DIR / f"{character}.csv"))
        frame = frame.dropna(subset=["Skill"]).copy()
        safe_frame = frame.astype(object).where(pd.notnull(frame), None)

        records: list[CalculatorRow] = []
        for record in safe_frame.to_dict("records"):
            skill = clean_text(record.get("Skill"))
            if not skill or skill.lower().startswith("skill tierlist"):
                continue
            record["Skill"] = skill
            records.append(record)

        default_attack = None
        for key in ("Test Basic Attack Dmg", "Base Attack", "Test Basic Attack"):
            for record in records:
                value = parse_number(record.get(key))
                if value is not None and value > 0:
                    default_attack = value
                    break
            if default_attack is not None:
                break

        payloads[character] = {
            "default_attack": float(default_attack or 1000),
            "records": records,
            "skills": {record["Skill"]: record for record in records},
        }

    return payloads


CALCULATOR_DATA: dict[str, CalculatorPayload] = load_calculator_data()


def skill_options_for(character: str) -> list[SkillOption]:
    """Build the dropdown option list for a character's skills, sorted alphabetically."""

    return sorted(
        [{"label": record["Skill"], "value": record["Skill"]} for record in CALCULATOR_DATA[character]["records"]],
        key=lambda option: option["label"].lower(),
    )


def get_row(character: str, skill: str | None) -> CalculatorRow:
    """Return the selected skill row, falling back to the character default."""

    skills: dict[str, CalculatorRow] = CALCULATOR_DATA[character]["skills"]
    if skill in skills:
        return skills[skill]

    fallback_skill = DEFAULT_SKILLS.get(character)
    if fallback_skill in skills:
        return skills[fallback_skill]

    return CALCULATOR_DATA[character]["records"][0]


def parse_rank_requirement(value: str) -> str | None:
    """Extract a Verso rank requirement from a condition label."""

    match = re.search(r"\b([DCBAS])\b", clean_text(value))
    if not match:
        return None
    rank = match.group(1)
    return rank if rank in RANK_ORDER else None


def rank_at_least(current_rank: str, required_rank: str | None) -> bool:
    """Check whether the current Verso rank satisfies a rank gate."""

    if required_rank is None:
        return False
    return RANK_ORDER.get(current_rank, -1) >= RANK_ORDER.get(required_rank, 99)


def build_sheet_rows(row: CalculatorRow) -> list[SheetScenario]:
    """Collect the distinct sheet breakpoints shown in the summary card."""

    entries: list[SheetScenario] = []

    def add_entry(label: str, value: float | None) -> None:
        if value is None:
            return
        if any(existing["label"] == label and existing["value"] == value for existing in entries):
            return
        entries.append({"label": label, "value": value})

    add_entry("Base", number_from_row(row, "Damage Multi"))

    conditional_value = number_from_row(row, "Dmg Con1", "ConDmg")
    conditional_label = text_from_row(row, "Condition 1", "Condition")
    if conditional_value is not None and conditional_value != number_from_row(row, "Damage Multi"):
        add_entry(conditional_label or "Conditional", conditional_value)

    maelle_value = number_from_row(row, "DmMax")
    maelle_label = text_from_row(row, "Condition")
    if maelle_value is not None and maelle_value != number_from_row(row, "Damage Multi"):
        add_entry(maelle_label or "Maximum", maelle_value)

    max_value = number_from_row(row, "Dmg Max", "TwilightDmg", "SRankMAX")
    max_label = text_from_row(row, "Con Max Dmg", "ConTwilight")
    if max_value is not None:
        if "TwilightDmg" in row and max_value == number_from_row(row, "TwilightDmg"):
            add_entry(max_label or "Twilight", max_value)
        elif "SRankMAX" in row and max_value == number_from_row(row, "SRankMAX"):
            add_entry(max_label or "S Rank", max_value)
        elif max_value != number_from_row(row, "Damage Multi"):
            add_entry(max_label or "Maximum", max_value)

    return entries


def calculate_current_cost(character: str, row: CalculatorRow, state: CalculatorState) -> str:
    """Return the displayed AP cost after character-specific modifiers."""

    raw_cost = clean_text(row.get("Cost"))
    numeric_cost = parse_number(row.get("Cost"))
    skill = clean_text(row.get("Skill"))

    if numeric_cost is None:
        return raw_cost or "-"

    if character == "maelle" and state.get("stance") == "Virtuoso" and skill in {"Momentum Strike", "Percee"}:
        return format_value(max(numeric_cost - 3, 0))

    if character == "verso":
        rank = clean_text(state.get("rank")) or "D"
        if skill in {"Follow Up", "Ascending Assault"} and rank == "S":
            return "2"
        if skill == "Perfect Break" and rank_at_least(rank, "B"):
            return "5"

    return format_value(numeric_cost)
