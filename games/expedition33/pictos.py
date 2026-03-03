from __future__ import annotations

from typing import Any, Literal, TypedDict

PictoControl = Literal[
    "attack_type",
    "below_10_health",
    "target_burning",
    "target_stunned",
    "exhausted",
    "full_health",
    "unhit",
    "inverted",
    "consume_ap",
    "shield_points",
    "fighting_alone",
    "all_allies_alive",
    "status_effects",
    "dodge_stacks",
    "parry_stacks",
    "warming_up_stacks",
    "first_hit",
]


class PictoDefinition(TypedDict, total=False):
    effect: str
    kind: Literal["always", "boolean", "stacks", "positive_numeric", "attack_type"]
    factor: float
    control: PictoControl
    attack_type: str
    rate: float
    max_stacks: int


class PictoStatus(TypedDict):
    name: str
    effect: str
    detail: str
    factor: float | None
    applied: bool


class PictoSummary(TypedDict):
    total_factor: float
    active: list[PictoStatus]
    inactive: list[PictoStatus]


PICTO_DEFINITIONS: dict[str, PictoDefinition] = {
    "At Death's Door": {
        "effect": "Deal 50% more damage if Health is below 10%.",
        "kind": "boolean",
        "factor": 1.5,
        "control": "below_10_health",
    },
    "Augmented Aim": {
        "effect": "50% increased Free Aim damage.",
        "kind": "attack_type",
        "factor": 1.5,
        "attack_type": "Free Aim",
    },
    "Augmented Attack": {
        "effect": "50% increased Base Attack damage.",
        "kind": "attack_type",
        "factor": 1.5,
        "attack_type": "Base Attack",
    },
    "Augmented Counter I": {
        "effect": "35% increased Counterattack damage.",
        "kind": "attack_type",
        "factor": 1.35,
        "attack_type": "Counterattack",
    },
    "Augmented Counter II": {
        "effect": "50% increased Counterattack damage.",
        "kind": "attack_type",
        "factor": 1.5,
        "attack_type": "Counterattack",
    },
    "Augmented Counter III": {
        "effect": "75% increased Counterattack damage.",
        "kind": "attack_type",
        "factor": 1.75,
        "attack_type": "Counterattack",
    },
    "Augmented First Strike": {
        "effect": "50% increased damage on the first hit once per battle.",
        "kind": "boolean",
        "factor": 1.5,
        "control": "first_hit",
    },
    "Break Specialist": {
        "effect": "Break damage is increased by 50%, but base damage is reduced by 20%.",
        "kind": "always",
        "factor": 0.8,
    },
    "Burn Affinity": {
        "effect": "25% increased damage on burning targets.",
        "kind": "boolean",
        "factor": 1.25,
        "control": "target_burning",
    },
    "Confident Fighter": {
        "effect": "30% increased damage, but can't be Healed.",
        "kind": "always",
        "factor": 1.3,
    },
    "Empowering Dodge": {
        "effect": "5% increased damage for each consecutive successful Dodge, up to 10 stacks.",
        "kind": "stacks",
        "rate": 0.05,
        "control": "dodge_stacks",
        "max_stacks": 10,
    },
    "Empowering Parry": {
        "effect": "Each successful Parry increases damage by 5% until end of the following turn.",
        "kind": "stacks",
        "rate": 0.05,
        "control": "parry_stacks",
    },
    "Exhausting Power": {
        "effect": "50% increased damage if Exhausted.",
        "kind": "boolean",
        "factor": 1.5,
        "control": "exhausted",
    },
    "Faster Than Strong": {
        "effect": "Deal 50% less damage.",
        "kind": "always",
        "factor": 0.5,
    },
    "First Offensive": {
        "effect": "The first hit dealt and taken deals 50% more damage.",
        "kind": "boolean",
        "factor": 1.5,
        "control": "first_hit",
    },
    "Full Strength": {
        "effect": "25% increased damage on full Health.",
        "kind": "boolean",
        "factor": 1.25,
        "control": "full_health",
    },
    "Glass Canon": {
        "effect": "Deal 25% more damage, but take 25% more damage.",
        "kind": "always",
        "factor": 1.25,
    },
    "Gradient Fighter": {
        "effect": "25% increased damage with Gradient Attacks.",
        "kind": "attack_type",
        "factor": 1.25,
        "attack_type": "Gradient Attack",
    },
    "Immaculate": {
        "effect": "30% increased damage until a hit is received.",
        "kind": "boolean",
        "factor": 1.3,
        "control": "unhit",
    },
    "Inverted Affinity": {
        "effect": "50% increased damage while Inverted.",
        "kind": "boolean",
        "factor": 1.5,
        "control": "inverted",
    },
    "Piercing Shot": {
        "effect": "25% increased Free Aim damage.",
        "kind": "attack_type",
        "factor": 1.25,
        "attack_type": "Free Aim",
    },
    "Powered Attack": {
        "effect": "If 1 AP is consumed on hit, increase damage by 20%.",
        "kind": "boolean",
        "factor": 1.2,
        "control": "consume_ap",
    },
    "Powerful Shield": {
        "effect": "10% increased damage per Shield Point on self.",
        "kind": "stacks",
        "rate": 0.1,
        "control": "shield_points",
    },
    "Shield Affinity": {
        "effect": "30% increased damage while having Shields.",
        "kind": "positive_numeric",
        "factor": 1.3,
        "control": "shield_points",
    },
    "Solo Fighter": {
        "effect": "Deal 50% more damage if fighting alone.",
        "kind": "boolean",
        "factor": 1.5,
        "control": "fighting_alone",
    },
    "Stun Boost": {
        "effect": "30% increased damage on stunned targets.",
        "kind": "boolean",
        "factor": 1.3,
        "control": "target_stunned",
    },
    "Tainted": {
        "effect": "15% increased damage for each Status Effect on self.",
        "kind": "stacks",
        "rate": 0.15,
        "control": "status_effects",
    },
    "Teamwork": {
        "effect": "10% increased damage while all allies are alive.",
        "kind": "boolean",
        "factor": 1.1,
        "control": "all_allies_alive",
    },
    "Warming Up": {
        "effect": "5% increased damage per turn, up to 5 stacks.",
        "kind": "stacks",
        "rate": 0.05,
        "control": "warming_up_stacks",
        "max_stacks": 5,
    },
}

PICTO_OPTIONS = [
    {"label": name, "value": name}
    for name in sorted(PICTO_DEFINITIONS, key=str.lower)
]

CONTROL_REASONS: dict[PictoControl, str] = {
    "all_allies_alive": "needs all allies alive",
    "attack_type": "needs a different attack type",
    "below_10_health": "needs Health below 10%",
    "consume_ap": "needs 1 AP to be consumed on hit",
    "dodge_stacks": "needs at least 1 Dodge stack",
    "exhausted": "needs Exhausted",
    "fighting_alone": "needs the character to be alone",
    "first_hit": "needs the first hit",
    "full_health": "needs full Health",
    "inverted": "needs Inverted",
    "parry_stacks": "needs at least 1 Parry stack",
    "shield_points": "needs at least 1 Shield Point",
    "status_effects": "needs at least 1 Status Effect on self",
    "target_burning": "needs a burning target",
    "target_stunned": "needs a stunned target",
    "unhit": "needs no hit received yet",
    "warming_up_stacks": "needs at least 1 Warming Up stack",
}


def _coerce_int(value: Any) -> int:
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


def _format_percent(factor: float) -> str:
    delta = round((factor - 1) * 100)
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta}%"


def _status_detail(name: str, factor: float, extra: str | None = None) -> str:
    detail = _format_percent(factor)
    if extra:
        detail = f"{detail} | {extra}"
    return f"{name} ({detail})"


def required_picto_controls(selected_pictos: list[str] | None) -> set[PictoControl]:
    controls: set[PictoControl] = set()
    for name in selected_pictos or []:
        definition = PICTO_DEFINITIONS.get(name)
        if not definition:
            continue
        control = definition.get("control")
        if control:
            controls.add(control)
        if definition.get("kind") == "attack_type":
            controls.add("attack_type")
    return controls


def evaluate_pictos(selected_pictos: list[str] | None, state: dict[str, Any]) -> PictoSummary:
    active: list[PictoStatus] = []
    inactive: list[PictoStatus] = []
    total_factor = 1.0

    for name in selected_pictos or []:
        definition = PICTO_DEFINITIONS.get(name)
        if not definition:
            continue

        effect = definition["effect"]
        kind = definition["kind"]
        applied = False
        factor: float | None = None
        detail = ""

        if kind == "always":
            factor = definition["factor"]
            applied = True
            detail = _status_detail(name, factor)

        elif kind == "boolean":
            control = definition["control"]
            if bool(state.get(control)):
                factor = definition["factor"]
                applied = True
                detail = _status_detail(name, factor)
            else:
                detail = f"{name} ({CONTROL_REASONS[control]})"

        elif kind == "attack_type":
            attack_type = str(state.get("attack_type") or "Skill")
            if attack_type == definition["attack_type"]:
                factor = definition["factor"]
                applied = True
                detail = _status_detail(name, factor, attack_type)
            else:
                detail = f"{name} (needs {definition['attack_type']})"

        elif kind == "positive_numeric":
            control = definition["control"]
            amount = _coerce_int(state.get(control))
            if amount > 0:
                factor = definition["factor"]
                applied = True
                detail = _status_detail(name, factor, f"{amount} Shield Point(s)")
            else:
                detail = f"{name} ({CONTROL_REASONS[control]})"

        elif kind == "stacks":
            control = definition["control"]
            amount = _coerce_int(state.get(control))
            max_stacks = definition.get("max_stacks")
            stacks = min(amount, max_stacks) if max_stacks is not None else amount
            if stacks > 0:
                factor = 1 + (definition["rate"] * stacks)
                applied = True
                detail = _status_detail(name, factor, f"{stacks} stack(s)")
            else:
                detail = f"{name} ({CONTROL_REASONS[control]})"

        status: PictoStatus = {
            "name": name,
            "effect": effect,
            "detail": detail,
            "factor": factor,
            "applied": applied,
        }
        if applied and factor is not None:
            total_factor *= factor
            active.append(status)
        else:
            inactive.append(status)

    return {
        "total_factor": total_factor,
        "active": active,
        "inactive": inactive,
    }
