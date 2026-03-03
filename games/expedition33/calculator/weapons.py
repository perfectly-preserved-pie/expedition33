from __future__ import annotations
from games.expedition33.calculator.core import CalculatorRow, clean_text
from typing import Any, Literal, TypedDict

WeaponControl = Literal[
    "attack_type",
    "shield_points",
    "unhit_turns",
    "stain_consume_stacks",
    "light_stains",
    "dark_stains",
    "self_burn_stacks",
    "foretell",
    "twilight",
    "moon_charges",
    "cursed",
    "ap_consumed",
    "critical_hit",
    "monoco_mask_type",
]

WeaponKind = Literal["fixed", "stacks", "suppress_verso_rank_bonus"]


class WeaponEffect(TypedDict, total=False):
    level: int
    effect: str
    kind: WeaponKind
    factor: float
    rate: float
    control: WeaponControl
    max_stacks: int
    attack_type: str
    required_boolean_control: WeaponControl
    required_numeric_control: WeaponControl
    required_numeric_min: int
    required_match_control: WeaponControl
    required_match_value: str
    forbidden_match_control: WeaponControl
    forbidden_match_value: str
    required_rank: str
    row_key: str
    row_value: str


class WeaponStatus(TypedDict):
    name: str
    effect: str
    detail: str
    factor: float | None
    applied: bool
    level: int


class WeaponSummary(TypedDict):
    total_factor: float
    active: list[WeaponStatus]
    inactive: list[WeaponStatus]
    suppress_verso_rank_bonus: bool


WEAPON_LEVEL_OPTIONS = [
    {"label": "No passives", "value": "0"},
    {"label": "Level 4", "value": "4"},
    {"label": "Level 10", "value": "10"},
    {"label": "Level 20", "value": "20"},
]

WEAPON_DEFINITIONS: dict[str, dict[str, list[WeaponEffect]]] = {
    "gustave": {
        "Abysseram": [
            {
                "level": 10,
                "effect": "50% increased Base Attack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Base Attack",
            },
        ],
        "Chevalam": [
            {
                "level": 10,
                "effect": "20% increased damage for each consecutive turn without taking damage, up to 5 stacks.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "unhit_turns",
                "max_stacks": 5,
            },
        ],
        "Dreameso": [
            {
                "level": 10,
                "effect": "50% increased Counterattack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Counterattack",
            },
        ],
        "Dualiso": [
            {
                "level": 10,
                "effect": "50% increased Base Attack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Base Attack",
            },
        ],
        "Liteso": [
            {
                "level": 4,
                "effect": "Base Attack consumes all Shields to deal 100% increased damage per Shield.",
                "kind": "stacks",
                "rate": 1.0,
                "control": "shield_points",
                "attack_type": "Base Attack",
            },
        ],
        "Nosaram": [
            {
                "level": 20,
                "effect": "50% increased Free Aim damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Free Aim",
            },
        ],
        "Sakaram": [
            {
                "level": 10,
                "effect": "50% increased Base Attack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Base Attack",
            },
        ],
    },
    "lune": {
        "Betelim": [
            {
                "level": 4,
                "effect": "Consuming Stains increases damage by 20%, up to 5 stacks.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "stain_consume_stacks",
                "max_stacks": 5,
            },
        ],
        "Choralim": [
            {
                "level": 10,
                "effect": "20% increased damage for each consecutive turn without taking damage, up to 5 stacks.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "unhit_turns",
                "max_stacks": 5,
            },
        ],
        "Colim": [
            {
                "level": 20,
                "effect": "20% increased Skill damage per active Light Stain.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "light_stains",
                "attack_type": "Skill",
            },
        ],
        "Lithelim": [
            {
                "level": 4,
                "effect": "50% more Skill damage per active Dark Stain.",
                "kind": "stacks",
                "rate": 0.5,
                "control": "dark_stains",
                "attack_type": "Skill",
            },
            {
                "level": 20,
                "effect": "Base Attacks can consume one Dark Stain to deal 200% more damage.",
                "kind": "fixed",
                "factor": 3.0,
                "attack_type": "Base Attack",
                "required_numeric_control": "dark_stains",
                "required_numeric_min": 1,
            },
        ],
        "Saperim": [
            {
                "level": 20,
                "effect": "Gradient Attacks deal 50% more damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Gradient Attack",
            },
        ],
        "Scaverim": [
            {
                "level": 4,
                "effect": "50% more Skill damage per active Dark Stain.",
                "kind": "stacks",
                "rate": 0.5,
                "control": "dark_stains",
                "attack_type": "Skill",
            },
            {
                "level": 10,
                "effect": "Base Attacks can consume one Dark Stain to deal 200% more damage.",
                "kind": "fixed",
                "factor": 3.0,
                "attack_type": "Base Attack",
                "required_numeric_control": "dark_stains",
                "required_numeric_min": 1,
            },
            {
                "level": 20,
                "effect": "With 4 active Dark Stains, Skills can consume them to deal 300% more damage.",
                "kind": "fixed",
                "factor": 4.0,
                "attack_type": "Skill",
                "required_numeric_control": "dark_stains",
                "required_numeric_min": 4,
            },
        ],
        "Troubadim": [
            {
                "level": 10,
                "effect": "50% increased Free Aim damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Free Aim",
            },
        ],
    },
    "maelle": {
        "Chalium": [
            {
                "level": 20,
                "effect": "50% increased Counter damage per Shield.",
                "kind": "stacks",
                "rate": 0.5,
                "control": "shield_points",
                "attack_type": "Counterattack",
            },
        ],
        "Jarum": [
            {
                "level": 20,
                "effect": "50% increased Counter damage per Shield.",
                "kind": "stacks",
                "rate": 0.5,
                "control": "shield_points",
                "attack_type": "Counterattack",
            },
        ],
        "Stalum": [
            {
                "level": 4,
                "effect": "10% increased damage for each self Burn stack.",
                "kind": "stacks",
                "rate": 0.1,
                "control": "self_burn_stacks",
            },
        ],
    },
    "monoco": {
        "Fragaro": [
            {
                "level": 10,
                "effect": "Free Aim shots deal 100% more damage with all Masks except Almighty.",
                "kind": "fixed",
                "factor": 2.0,
                "attack_type": "Free Aim",
                "forbidden_match_control": "monoco_mask_type",
                "forbidden_match_value": "Almighty",
            },
        ],
        "Joyaro": [
            {
                "level": 10,
                "effect": "20% increased damage for each consecutive turn without taking damage, up to 5 stacks.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "unhit_turns",
                "max_stacks": 5,
            },
        ],
        "Monocaro": [
            {
                "level": 20,
                "effect": "Critical hits deal 30% more damage while in Balanced Mask.",
                "kind": "fixed",
                "factor": 1.3,
                "required_boolean_control": "critical_hit",
                "required_match_control": "monoco_mask_type",
                "required_match_value": "Balanced",
            },
        ],
    },
    "sciel": {
        "Algueron": [
            {
                "level": 4,
                "effect": "Free Aim shots can consume 1 Foretell to deal 100% more damage.",
                "kind": "fixed",
                "factor": 2.0,
                "attack_type": "Free Aim",
                "required_numeric_control": "foretell",
                "required_numeric_min": 1,
            },
            {
                "level": 20,
                "effect": "During Twilight, Free Aim shots deal double damage.",
                "kind": "fixed",
                "factor": 2.0,
                "attack_type": "Free Aim",
                "required_boolean_control": "twilight",
            },
        ],
        "Blizzon": [
            {
                "level": 10,
                "effect": "25% increased damage per Moon charge.",
                "kind": "stacks",
                "rate": 0.25,
                "control": "moon_charges",
            },
        ],
        "Charnon": [
            {
                "level": 20,
                "effect": "20% increased damage for each consecutive turn without taking damage, up to 5 stacks.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "unhit_turns",
                "max_stacks": 5,
            },
        ],
        "Corderon": [
            {
                "level": 4,
                "effect": "Deal 50% more damage while Cursed.",
                "kind": "fixed",
                "factor": 1.5,
                "required_boolean_control": "cursed",
            },
        ],
        "Direton": [
            {
                "level": 20,
                "effect": "During Twilight, Base Attack deals 50% increased damage per AP consumed.",
                "kind": "stacks",
                "rate": 0.5,
                "control": "ap_consumed",
                "attack_type": "Base Attack",
                "required_boolean_control": "twilight",
            },
        ],
        "Hevasson": [
            {
                "level": 4,
                "effect": "Free Aim shots can consume a Moon charge to deal 400% more damage.",
                "kind": "fixed",
                "factor": 5.0,
                "attack_type": "Free Aim",
                "required_numeric_control": "moon_charges",
                "required_numeric_min": 1,
            },
        ],
        "Tisseron": [
            {
                "level": 4,
                "effect": "Sun Skills deal 50% more damage.",
                "kind": "fixed",
                "factor": 1.5,
                "row_key": "Lunar",
                "row_value": "Sun",
            },
        ],
    },
    "verso": {
        "Abysseram": [
            {
                "level": 4,
                "effect": "50% increased damage on Rank D.",
                "kind": "fixed",
                "factor": 1.5,
                "required_rank": "D",
            },
            {
                "level": 10,
                "effect": "50% increased Base Attack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Base Attack",
            },
        ],
        "Chevalam": [
            {
                "level": 10,
                "effect": "20% increased damage for each consecutive turn without taking damage, up to 5 stacks.",
                "kind": "stacks",
                "rate": 0.2,
                "control": "unhit_turns",
                "max_stacks": 5,
            },
        ],
        "Dreameso": [
            {
                "level": 10,
                "effect": "50% increased Counterattack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Counterattack",
            },
        ],
        "Dualiso": [
            {
                "level": 10,
                "effect": "50% increased Base Attack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Base Attack",
            },
        ],
        "Liteso": [
            {
                "level": 4,
                "effect": "Base Attack consumes all Shields to deal 100% increased damage per Shield.",
                "kind": "stacks",
                "rate": 1.0,
                "control": "shield_points",
                "attack_type": "Base Attack",
            },
        ],
        "Nosaram": [
            {
                "level": 20,
                "effect": "50% increased Free Aim damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Free Aim",
            },
        ],
        "Sakaram": [
            {
                "level": 4,
                "effect": "No damage increase from Rank.",
                "kind": "suppress_verso_rank_bonus",
            },
            {
                "level": 10,
                "effect": "50% increased Base Attack damage.",
                "kind": "fixed",
                "factor": 1.5,
                "attack_type": "Base Attack",
            },
        ],
        "Sireso": [
            {
                "level": 4,
                "effect": "Bonus damage from Perfection no longer applies to Verso.",
                "kind": "suppress_verso_rank_bonus",
            },
        ],
    },
}

WEAPON_OPTIONS = {
    character: [{"label": name, "value": name} for name in sorted(definitions, key=str.lower)]
    for character, definitions in WEAPON_DEFINITIONS.items()
}

BONUS_CONTROLS: set[WeaponControl] = {
    "attack_type",
    "shield_points",
    "unhit_turns",
    "stain_consume_stacks",
    "light_stains",
    "dark_stains",
    "self_burn_stacks",
    "moon_charges",
    "cursed",
    "ap_consumed",
    "critical_hit",
    "monoco_mask_type",
}

CONTROL_REASONS: dict[WeaponControl, str] = {
    "ap_consumed": "needs at least 1 AP to be consumed",
    "attack_type": "needs a different attack type",
    "critical_hit": "needs a Critical Hit",
    "cursed": "needs Cursed",
    "dark_stains": "needs at least 1 Dark Stain",
    "foretell": "needs at least 1 Foretell",
    "light_stains": "needs at least 1 Light Stain",
    "monoco_mask_type": "needs a different Mask",
    "moon_charges": "needs at least 1 Moon charge",
    "self_burn_stacks": "needs at least 1 self Burn stack",
    "shield_points": "needs at least 1 Shield Point",
    "stain_consume_stacks": "needs at least 1 stain-consume stack",
    "twilight": "needs Twilight",
    "unhit_turns": "needs at least 1 no-hit stack",
}

STACK_LABELS: dict[WeaponControl, str] = {
    "ap_consumed": "AP",
    "dark_stains": "Dark Stain(s)",
    "foretell": "Foretell",
    "light_stains": "Light Stain(s)",
    "moon_charges": "Moon charge(s)",
    "self_burn_stacks": "self Burn stack(s)",
    "shield_points": "Shield Point(s)",
    "stain_consume_stacks": "stack(s)",
    "unhit_turns": "stack(s)",
}

BOOLEAN_LABELS: dict[WeaponControl, str] = {
    "critical_hit": "Critical Hit",
    "cursed": "Cursed",
    "twilight": "Twilight",
}

CHARACTER_CONTROL_MAP = {
    "foretell": "sciel_foretell",
    "twilight": "sciel_twilight",
}


def normalize_weapon_level(value: str | int | None) -> int:
    """Normalize a weapon-level selection to one of the supported unlock tiers."""

    try:
        level = int(value or 0)
    except (TypeError, ValueError):
        return 0

    if level >= 20:
        return 20
    if level >= 10:
        return 10
    if level >= 4:
        return 4
    return 0


def weapon_options_for(character: str) -> list[dict[str, str]]:
    """Return the supported weapon options for a character."""

    return WEAPON_OPTIONS.get(character, [])


def _coerce_int(value: Any) -> int:
    """Convert a raw control value into a non-negative integer."""

    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


def _format_percent(factor: float) -> str:
    """Format a multiplier as a signed percent delta."""

    delta = round((factor - 1) * 100)
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta}%"


def _status_detail(name: str, level: int, factor: float, extra: str | None = None) -> str:
    """Build the short status label shown in the result summary."""

    detail = _format_percent(factor)
    if extra:
        detail = f"{detail} | {extra}"
    return f"{name} Lv.{level} ({detail})"


def _locked_detail(name: str, level: int) -> str:
    """Describe a passive that is still locked behind weapon level."""

    return f"{name} Lv.{level} (needs weapon level {level})"


def _current_rank(state: dict[str, Any]) -> str:
    """Read the current Verso rank from weapon state."""

    return clean_text(state.get("rank")) or "D"


def _verso_rank_bonus_active(state: dict[str, Any]) -> bool:
    """Check whether Verso's generic rank multiplier is currently active."""

    return _current_rank(state) in {"C", "B", "A", "S"}


def _stack_extra(control: WeaponControl, amount: int) -> str:
    """Format the numeric context for a stack-based weapon passive."""

    label = STACK_LABELS.get(control, "stack(s)")
    return f"{amount} {label}"


def _condition_extra(effect: WeaponEffect, row: CalculatorRow, state: dict[str, Any], stack_value: int | None = None) -> str | None:
    """Build a concise detail suffix for an applied weapon passive."""

    extras: list[str] = []

    if effect.get("attack_type"):
        extras.append(str(effect["attack_type"]))
    if effect.get("required_rank"):
        extras.append(f"Rank {effect['required_rank']}")
    if effect.get("row_key") and effect.get("row_value"):
        if effect["row_key"] == "Lunar":
            extras.append(f"{effect['row_value']} Skill")
        else:
            extras.append(f"{effect['row_key']}: {effect['row_value']}")
    if effect.get("required_boolean_control"):
        label = BOOLEAN_LABELS.get(effect["required_boolean_control"])
        if label:
            extras.append(label)
    if effect.get("required_numeric_control"):
        control = effect["required_numeric_control"]
        amount = _coerce_int(state.get(control))
        extras.append(_stack_extra(control, amount))
    if effect.get("required_match_control") and effect.get("required_match_value"):
        if effect["required_match_control"] == "monoco_mask_type":
            extras.append(f"{effect['required_match_value']} Mask")
        else:
            extras.append(str(effect["required_match_value"]))
    if effect.get("forbidden_match_control") == "monoco_mask_type":
        mask_type = clean_text(state.get("monoco_mask_type")) or "Balanced"
        extras.append(f"{mask_type} Mask")
    if stack_value is not None and effect.get("control"):
        extras.append(_stack_extra(effect["control"], stack_value))

    return ", ".join(extras) if extras else None


def _inactive_reason(effect: WeaponEffect, row: CalculatorRow, state: dict[str, Any]) -> str:
    """Describe why a weapon passive is not active for the current state."""

    attack_type = effect.get("attack_type")
    if attack_type:
        current_attack_type = clean_text(state.get("attack_type")) or "Skill"
        if current_attack_type != attack_type:
            return f"needs {attack_type}"

    required_rank = effect.get("required_rank")
    if required_rank and _current_rank(state) != required_rank:
        return f"needs Verso Rank {required_rank}"

    row_key = effect.get("row_key")
    row_value = effect.get("row_value")
    if row_key and row_value and clean_text(row.get(row_key)) != row_value:
        if row_key == "Lunar":
            return f"needs a {row_value} Skill"
        return f"needs {row_key}={row_value}"

    required_boolean = effect.get("required_boolean_control")
    if required_boolean and not bool(state.get(required_boolean)):
        return CONTROL_REASONS[required_boolean]

    required_numeric = effect.get("required_numeric_control")
    if required_numeric:
        minimum = int(effect.get("required_numeric_min", 1))
        amount = _coerce_int(state.get(required_numeric))
        if amount < minimum:
            if minimum > 1:
                return f"needs at least {minimum} {STACK_LABELS.get(required_numeric, 'stack(s)')}"
            return CONTROL_REASONS[required_numeric]

    required_match = effect.get("required_match_control")
    required_value = effect.get("required_match_value")
    if required_match and required_value:
        current_value = clean_text(state.get(required_match))
        if current_value != required_value:
            if required_match == "monoco_mask_type":
                return f"needs {required_value} Mask"
            return f"needs {required_value}"

    forbidden_match = effect.get("forbidden_match_control")
    forbidden_value = effect.get("forbidden_match_value")
    if forbidden_match and forbidden_value and clean_text(state.get(forbidden_match)) == forbidden_value:
        if forbidden_match == "monoco_mask_type":
            return f"needs a non-{forbidden_value} Mask"
        return f"cannot be {forbidden_value}"

    if effect["kind"] == "stacks":
        control = effect["control"]
        amount = _coerce_int(state.get(control))
        if amount <= 0:
            return CONTROL_REASONS[control]

    if effect["kind"] == "suppress_verso_rank_bonus" and not _verso_rank_bonus_active(state):
        return "Verso rank bonus is not active"

    return "needs matching setup"


def required_weapon_controls(character: str, weapon: str | None, weapon_level: str | int | None) -> set[WeaponControl]:
    """Determine which bonus-setup controls are needed for a selected weapon."""

    definitions = WEAPON_DEFINITIONS.get(character, {}).get(weapon or "", [])
    unlocked_level = normalize_weapon_level(weapon_level)
    controls: set[WeaponControl] = set()

    for effect in definitions:
        if effect["level"] > unlocked_level:
            continue
        if effect.get("attack_type"):
            controls.add("attack_type")
        for key in ("control", "required_boolean_control", "required_numeric_control", "required_match_control", "forbidden_match_control"):
            control = effect.get(key)
            if control in BONUS_CONTROLS:
                controls.add(control)

    return controls


def required_weapon_character_controls(character: str, weapon: str | None, weapon_level: str | int | None) -> set[str]:
    """Determine which existing character controls a selected weapon needs."""

    definitions = WEAPON_DEFINITIONS.get(character, {}).get(weapon or "", [])
    unlocked_level = normalize_weapon_level(weapon_level)
    controls: set[str] = set()

    for effect in definitions:
        if effect["level"] > unlocked_level:
            continue
        if effect["kind"] == "suppress_verso_rank_bonus" or effect.get("required_rank"):
            controls.add("verso_rank")
        for key in ("required_boolean_control", "required_numeric_control"):
            control = effect.get(key)
            if control in CHARACTER_CONTROL_MAP:
                controls.add(CHARACTER_CONTROL_MAP[control])

    return controls


def evaluate_weapon(
    character: str,
    selected_weapon: str | None,
    weapon_level: str | int | None,
    row: CalculatorRow,
    state: dict[str, Any],
) -> WeaponSummary:
    """Evaluate a selected weapon's unlocked passives against the UI state."""

    if not selected_weapon:
        return {
            "total_factor": 1.0,
            "active": [],
            "inactive": [],
            "suppress_verso_rank_bonus": False,
        }

    definitions = WEAPON_DEFINITIONS.get(character, {}).get(selected_weapon, [])
    unlocked_level = normalize_weapon_level(weapon_level)
    active: list[WeaponStatus] = []
    inactive: list[WeaponStatus] = []
    total_factor = 1.0
    suppress_verso_rank_bonus = False

    for effect in definitions:
        level = effect["level"]
        if level > unlocked_level:
            inactive.append(
                {
                    "name": selected_weapon,
                    "effect": effect["effect"],
                    "detail": _locked_detail(selected_weapon, level),
                    "factor": None,
                    "applied": False,
                    "level": level,
                }
            )
            continue

        kind = effect["kind"]
        factor: float | None = None
        applied = False
        detail = ""

        if kind == "suppress_verso_rank_bonus":
            applied = character == "verso" and _verso_rank_bonus_active(state)
            detail = (
                f"{selected_weapon} Lv.{level} (suppresses Verso rank bonus)"
                if applied
                else f"{selected_weapon} Lv.{level} ({_inactive_reason(effect, row, state)})"
            )
            if applied:
                suppress_verso_rank_bonus = True

        else:
            reason = _inactive_reason(effect, row, state)
            if reason == "needs matching setup":
                if kind == "fixed":
                    factor = effect["factor"]
                    applied = True
                    detail = _status_detail(
                        selected_weapon,
                        level,
                        factor,
                        _condition_extra(effect, row, state),
                    )
                elif kind == "stacks":
                    amount = _coerce_int(state.get(effect["control"]))
                    max_stacks = effect.get("max_stacks")
                    stacks = min(amount, max_stacks) if max_stacks is not None else amount
                    if stacks > 0:
                        factor = 1 + (effect["rate"] * stacks)
                        applied = True
                        detail = _status_detail(
                            selected_weapon,
                            level,
                            factor,
                            _condition_extra(effect, row, state, stacks),
                        )
                    else:
                        detail = f"{selected_weapon} Lv.{level} ({CONTROL_REASONS[effect['control']]})"
            else:
                detail = f"{selected_weapon} Lv.{level} ({reason})"

        status: WeaponStatus = {
            "name": selected_weapon,
            "effect": effect["effect"],
            "detail": detail,
            "factor": factor,
            "applied": applied,
            "level": level,
        }
        if applied and factor is not None:
            total_factor *= factor
            active.append(status)
        elif applied:
            active.append(status)
        else:
            inactive.append(status)

    return {
        "total_factor": total_factor,
        "active": active,
        "inactive": inactive,
        "suppress_verso_rank_bonus": suppress_verso_rank_bonus,
    }
