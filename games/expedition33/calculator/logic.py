from __future__ import annotations
from games.expedition33.calculator.core import (
    CalculationResult,
    CalculatorRow,
    CalculatorState,
    ControlStyles,
    HIDDEN_STYLE,
    VISIBLE_STYLE,
    base_result,
    clamp_int,
    clean_text,
    extract_first_int,
    number_from_row,
    parse_rank_requirement,
    rank_at_least,
    result,
    text_from_row,
)
from games.expedition33.calculator.pictos import PictoSummary

SCIEL_FORETELL_RATES = {
    "End Slice": 0.20,
    "End Slice 30 Foretell": 0.20,
    "Twilight Dance": 0.25,
    "Phantom Blade": 0.35,
    "Dark Wave": 0.25,
    "Delaying Slash": 0.30,
    "Twilight Slash": 0.25,
}


def calculate_gustave(row: CalculatorRow, state: CalculatorState) -> CalculationResult:
    """Calculate Gustave skill damage from charge-based state."""

    skill = clean_text(row.get("Skill"))
    if skill.startswith("Overcharge"):
        charges = clamp_int(state.get("charges"), 0, 10)
        multiplier = 2.1 * (1 + (0.2 * charges))
        if charges >= 10:
            multiplier *= 1.25
        return result(round(multiplier, 2), f"{charges} Charges", "Derived from Overcharge note")

    return base_result(row)


def calculate_lune(row: CalculatorRow, state: CalculatorState) -> CalculationResult:
    """Calculate Lune skill damage from stain, turn, and crit state."""

    skill = clean_text(row.get("Skill"))
    base_multiplier = number_from_row(row, "Damage Multi")
    conditional = number_from_row(row, "Dmg Con1")
    maximum = number_from_row(row, "Dmg Max")
    condition = text_from_row(row, "Condition 1").lower()
    max_condition = text_from_row(row, "Con Max Dmg").lower()
    stains = clamp_int(state.get("stains"), 0, 4)
    turns = clamp_int(state.get("turns"), 1, 5)
    all_crits = bool(state.get("all_crits"))

    if skill.startswith("Burn "):
        ticks = clamp_int(state.get("turns"), 1, 3)
        return result(round((base_multiplier or 0) * ticks, 2), f"{ticks} Burn tick(s)", "Derived from burn rows")

    if condition == "turn start dmg" and stains > 0 and conditional is not None:
        total = round((base_multiplier or 0) + (conditional * turns), 2)
        return result(total, f"{turns} turn(s) with stains", "Derived from Damage Multi + Dmg Con1")

    if skill == "Fire Rage":
        if turns >= 3 and maximum is not None:
            return result(maximum, "Turn 3", "Dmg Max")
        if turns >= 2 and conditional is not None:
            return result(conditional, "Turn 2", "Dmg Con1")
        return base_result(row, "Turn 1")

    if skill == "Fire Rage Stained":
        if turns >= 3 and stains >= 1 and maximum is not None:
            return result(maximum, "Stained Turn 3", "Dmg Max")
        if turns >= 2 and stains >= 2 and conditional is not None:
            return result(conditional, "2 Stains on Turn 2", "Dmg Con1")
        return base_result(row, "Turn 1")

    max_threshold = extract_first_int(max_condition)
    cond_threshold = extract_first_int(condition)

    if maximum is not None:
        if "crit" in max_condition and all_crits and (max_threshold is None or stains >= max_threshold):
            return result(maximum, text_from_row(row, "Con Max Dmg") or "Maximum", "Dmg Max")
        if "burn" in max_condition and turns >= 3 and (max_threshold is None or stains >= max_threshold):
            return result(maximum, text_from_row(row, "Con Max Dmg") or "Maximum", "Dmg Max")
        if "t3" in max_condition and turns >= 3:
            return result(maximum, text_from_row(row, "Con Max Dmg") or "Maximum", "Dmg Max")
        if max_threshold is not None and "stain" in max_condition and stains >= max_threshold:
            return result(maximum, text_from_row(row, "Con Max Dmg") or "Maximum", "Dmg Max")

    if conditional is not None:
        if "t2" in condition and turns >= 2:
            return result(conditional, text_from_row(row, "Condition 1") or "Conditional", "Dmg Con1")
        if cond_threshold is not None and "stain" in condition and stains >= cond_threshold:
            return result(conditional, text_from_row(row, "Condition 1") or "Conditional", "Dmg Con1")
        if condition.startswith("grad"):
            return result(conditional, text_from_row(row, "Condition 1") or "Conditional", "Dmg Con1")

    return base_result(row)


def calculate_maelle(row: CalculatorRow, state: CalculatorState) -> CalculationResult:
    """Calculate Maelle skill damage from burn, marked, and hit-based state."""

    skill = clean_text(row.get("Skill"))
    base_multiplier = number_from_row(row, "Damage Multi")
    maximum = number_from_row(row, "DmMax")
    stance = clean_text(state.get("stance")) or "Stanceless"
    burn_stacks = clamp_int(state.get("burn_stacks"), 0, 100)
    hits_taken = clamp_int(state.get("hits_taken"), 0, 5)
    marked = bool(state.get("marked"))
    all_crits = bool(state.get("all_crits"))
    turns = clamp_int(state.get("turns"), 1, 3)

    def with_stance(skill_result: CalculationResult) -> CalculationResult:
        multiplier = skill_result.get("multiplier")
        stance_multiplier = {
            "Offensive": 1.5,
            "Virtuoso": 3.0,
        }.get(stance)

        if multiplier is None or stance_multiplier is None or skill.startswith("Burn "):
            return skill_result

        return result(
            round(multiplier * stance_multiplier, 2),
            f"{skill_result['scenario']} | {stance} stance",
            f"{skill_result['source']} + stance bonus",
            skill_result.get("warning"),
        )

    if skill == "Burning Canvas":
        multiplier = round((base_multiplier or 0) * (1 + (0.1 * burn_stacks)), 2)
        return with_stance(result(multiplier, f"{burn_stacks} Burn stack(s)", "Derived from note text"))

    if skill == "Combustion":
        multiplier = round((base_multiplier or 0) * (1 + (0.4 * min(burn_stacks, 10))), 2)
        return with_stance(result(multiplier, f"Consume {min(burn_stacks, 10)} Burn", "Derived from note text"))

    if skill == "Revenge":
        multiplier = round((base_multiplier or 0) * (1 + (1.5 * hits_taken)), 2)
        return with_stance(result(multiplier, f"{hits_taken} hit(s) taken last round", "Derived from note text"))

    if skill.startswith("Burn "):
        return result(round((base_multiplier or 0) * turns, 2), f"{turns} Burn tick(s)", "Derived from burn rows")

    if skill in {"G-Homage", "Momentum Strike", "Percee"} and marked and maximum is not None:
        return with_stance(result(maximum, "Marked target", "DmMax"))

    if skill == "Sword Ballet" and all_crits and maximum is not None:
        return with_stance(result(maximum, "All crits", "DmMax"))

    return with_stance(base_result(row))


def uses_mask_condition(row: CalculatorRow) -> bool:
    """Return whether a Monoco row's sheet data explicitly depends on mask state."""

    texts = (
        text_from_row(row, "Condition 1"),
        text_from_row(row, "Con Max Dmg"),
        text_from_row(row, "Notes"),
    )
    return any("mask" in text.lower() for text in texts if text)


def monoco_mask_type(row: CalculatorRow) -> str:
    """Return Monoco's mask type for rows that can receive generic mask bonuses."""

    return clean_text(row.get("Mask")).strip()


def has_explicit_monoco_mask_breakpoint(row: CalculatorRow) -> bool:
    """Return whether the sheet already provides a masked damage breakpoint."""

    texts = (
        text_from_row(row, "Condition 1"),
        text_from_row(row, "Con Max Dmg"),
    )
    return any("mask" in text.lower() for text in texts if text)


def can_apply_generic_monoco_mask_bonus(row: CalculatorRow) -> bool:
    """Return whether a Monoco row should use the fallback generic mask bonus."""

    mask_type = monoco_mask_type(row).upper()
    return bool(mask_type and mask_type != "GRADIENT" and not has_explicit_monoco_mask_breakpoint(row))


def apply_monoco_mask_bonus(row: CalculatorRow, skill_result: CalculationResult) -> CalculationResult:
    """Apply Monoco's generic mask bonus when the sheet lacks an explicit masked value."""

    multiplier = skill_result.get("multiplier")
    if multiplier is None or not can_apply_generic_monoco_mask_bonus(row):
        return skill_result

    mask_type = monoco_mask_type(row).upper()
    bonus_multiplier = 5.0 if mask_type == "ALMIGHTY" else 3.0
    label = "Almighty mask" if mask_type == "ALMIGHTY" else f"{monoco_mask_type(row)} mask"

    return result(
        round(multiplier * bonus_multiplier, 2),
        f"{skill_result['scenario']} | {label} bonus",
        f"{skill_result['source']} + generic mask bonus",
        skill_result.get("warning"),
    )


def calculate_monoco(row: CalculatorRow, state: CalculatorState) -> CalculationResult:
    """Calculate Monoco skill damage from mask and target status state."""

    skill = clean_text(row.get("Skill"))
    base_multiplier = number_from_row(row, "Damage Multi")
    conditional = number_from_row(row, "Dmg Con1")
    maximum = number_from_row(row, "Dmg Max")
    mask_active = bool(state.get("mask_active"))
    turns = clamp_int(state.get("turns"), 1, 3)
    stunned = bool(state.get("stunned"))
    marked = bool(state.get("marked"))
    powerless = bool(state.get("powerless"))
    burning = bool(state.get("burning"))
    low_life = bool(state.get("low_life"))
    full_life = bool(state.get("full_life"))
    all_crits = bool(state.get("all_crits"))

    def with_generic_mask(skill_result: CalculationResult) -> CalculationResult:
        if not mask_active:
            return skill_result
        return apply_monoco_mask_bonus(row, skill_result)

    if skill.startswith("Burn "):
        return result(round((base_multiplier or 0) * turns, 2), f"{turns} Burn tick(s)", "Derived from burn rows")

    if skill == "Mighty Strike" and stunned and maximum is not None:
        return result(maximum, "Stunned target", "Dmg Max")

    if skill == "Sakapate Estoc":
        if mask_active and stunned and maximum is not None:
            return result(maximum, "Masked and stunned", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Sakapate Fire":
        if mask_active and turns >= 3 and maximum is not None:
            return result(maximum, "Mask active with 3 Burn turns", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Cultist Slashes":
        if mask_active and low_life and maximum is not None:
            return result(maximum, "Mask active at low life", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Sakapate Slam":
        if mask_active and marked and maximum is not None:
            return result(maximum, "Masked and marked target", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Obscur Sword":
        if mask_active and powerless and maximum is not None:
            return result(maximum, "Masked and powerless target", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Danseuse Waltz":
        if mask_active and burning and maximum is not None:
            return result(maximum, "Mask active vs burning target", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Chevalier Thrusts":
        if mask_active and all_crits and maximum is not None:
            return result(maximum, "Mask active and all crits", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Sakapate Explosion":
        if mask_active and all_crits and maximum is not None:
            return result(maximum, "Mask active and all crits", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Cultist Blood":
        if mask_active and full_life and maximum is not None:
            return result(maximum, "Mask active at full life", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if skill == "Abberation Light":
        if mask_active and turns >= 3 and maximum is not None:
            return result(maximum, "Mask active with 3 Burn turns", "Dmg Max")
        if turns >= 3 and conditional is not None:
            return result(conditional, "3 Burn turns", "Dmg Con1")

    if skill == "Braseleur Smash":
        if mask_active and turns >= 3 and maximum is not None:
            return result(maximum, "Mask active with 3 Burn turns", "Dmg Max")
        if mask_active and conditional is not None:
            return result(conditional, "Mask active", "Dmg Con1")

    if mask_active and has_explicit_monoco_mask_breakpoint(row) and conditional is not None:
        return result(conditional, "Mask active", "Dmg Con1")

    return with_generic_mask(base_result(row))


def effective_sciel_foretell(foretell: int, twilight: bool) -> int:
    """Return Sciel's Twilight-adjusted foretell without imposing a global cap."""

    if twilight:
        return max(foretell, 0) * 2
    return max(foretell, 0)


def calculate_sciel(row: CalculatorRow, state: CalculatorState) -> CalculationResult:
    """Calculate Sciel skill damage from foretell, twilight, and life state."""

    skill = clean_text(row.get("Skill"))
    base_multiplier = number_from_row(row, "Damage Multi")
    conditional = number_from_row(row, "ConDmg")
    twilight_value = number_from_row(row, "TwilightDmg")
    foretell = max(clamp_int(state.get("foretell"), 0, 999), 0)
    twilight = bool(state.get("twilight"))
    full_life = bool(state.get("full_life"))
    effective_foretell = effective_sciel_foretell(foretell, twilight)

    if skill in SCIEL_FORETELL_RATES:
        rate = SCIEL_FORETELL_RATES[skill]
        multiplier = (base_multiplier or 0) * (1 + (rate * effective_foretell))
        scenario = f"{effective_foretell} Twilight-effective Foretell" if twilight else f"{foretell} Foretell"
        source = "Derived from note text"
        if twilight:
            multiplier *= 1.5
            scenario = f"{scenario} from {foretell} applied Foretell, Twilight"
            source = "Derived from note text + Twilight"
        return result(round(multiplier, 2), scenario, source)

    if skill == "Our Sacrifice":
        multiplier = (base_multiplier or 0) * (1 + (0.3 * effective_foretell))
        scenario_parts = [f"{effective_foretell} Twilight-effective Foretell" if twilight else f"{foretell} Foretell"]
        if full_life:
            multiplier *= 3.97
            scenario_parts.append("Full life")
        if twilight:
            multiplier *= 1.5
            scenario_parts.append(f"Twilight from {foretell} applied Foretell")
        return result(round(multiplier, 2), ", ".join(scenario_parts), "Derived from note text")

    if skill == "Sealed Fate":
        if foretell >= 1 and twilight and twilight_value is not None:
            return result(twilight_value, f"{effective_foretell} Twilight-effective Foretell, Twilight", "TwilightDmg")
        if foretell >= 1 and conditional is not None:
            return result(conditional, f"{foretell} Foretell", "ConDmg")
        return base_result(row)

    if skill == "Firing Shadow":
        consumed_foretell = min(effective_foretell, 3)
        multiplier = (base_multiplier or 0) * (1 + (consumed_foretell / 3))
        scenario = (
            f"{consumed_foretell} Twilight-effective Foretell consumed from {foretell} applied Foretell"
            if twilight
            else f"{consumed_foretell} Foretell consumed"
        )
        if twilight:
            multiplier *= 1.5
        return result(round(multiplier, 2), scenario, "Derived from note text")

    if twilight and twilight_value is not None:
        return result(twilight_value, f"Twilight from {foretell} applied Foretell", "TwilightDmg")

    return base_result(row)


def apply_verso_rank_bonus(rank: str, skill_result: CalculationResult) -> CalculationResult:
    """Apply Verso's general rank bonus unless the sheet value already includes it."""

    multiplier = skill_result.get("multiplier")
    source = skill_result.get("source", "")
    if multiplier is None or source == "SRankMAX":
        return skill_result

    rank_bonus = {
        "D": 1.0,
        "C": 1.25,
        "B": 1.5,
        "A": 2.0,
        "S": 3.0,
    }.get(rank, 1.0)

    if rank_bonus == 1.0:
        return skill_result

    return result(
        round(multiplier * rank_bonus, 2),
        f"{skill_result['scenario']} | {rank} Rank bonus",
        f"{source} + general rank bonus",
        skill_result.get("warning"),
    )


def calculate_verso(row: CalculatorRow, state: CalculatorState) -> CalculationResult:
    """Calculate Verso skill damage from rank and setup state."""

    skill = clean_text(row.get("Skill"))
    base_multiplier = number_from_row(row, "Damage Multi")
    conditional = number_from_row(row, "ConDmg")
    maximum = number_from_row(row, "SRankMAX")
    rank = clean_text(state.get("rank")) or "D"
    stunned = bool(state.get("stunned"))
    speed_bonus = bool(state.get("speed_bonus"))
    shots = clamp_int(state.get("shots"), 0, 10)
    uses = clamp_int(state.get("uses"), 1, 6)
    required_rank = parse_rank_requirement(text_from_row(row, "Condition"))

    if skill == "End Bringer":
        if stunned and rank == "S" and maximum is not None:
            return result(maximum, "Stunned target at S Rank", "SRankMAX")
        if stunned and conditional is not None:
            return apply_verso_rank_bonus(rank, result(conditional, "Stunned target", "ConDmg"))
        return apply_verso_rank_bonus(rank, base_result(row))

    if skill == "Steeled Strike":
        if rank == "S" and uses >= 2 and maximum is not None:
            return result(maximum, "S Rank with full setup", "SRankMAX")
        if rank == "S" and conditional is not None:
            return apply_verso_rank_bonus(rank, result(conditional, "S Rank", "ConDmg"))
        return apply_verso_rank_bonus(rank, base_result(row))

    if skill == "Follow Up":
        if rank == "S" and shots >= 10 and maximum is not None:
            return result(maximum, "10 shots at S Rank", "SRankMAX")
        if shots > 0:
            multiplier = round((base_multiplier or 0) * (1 + (0.5 * shots)), 2)
            return apply_verso_rank_bonus(rank, result(multiplier, f"{shots} ranged shot(s)", "Derived from note text"))
        return apply_verso_rank_bonus(rank, base_result(row))

    if skill == "Ascending Assault":
        if rank == "S" and uses >= 6 and maximum is not None:
            return result(maximum, "6th use at S Rank", "SRankMAX")
        if uses >= 2:
            multiplier = round((base_multiplier or 0) * (1 + (0.3 * min(uses - 1, 5))), 2)
            if uses >= 6 and conditional is not None:
                return apply_verso_rank_bonus(rank, result(conditional, "6th use", "ConDmg"))
            return apply_verso_rank_bonus(rank, result(multiplier, f"Use {uses}", "Derived from note text"))
        return apply_verso_rank_bonus(rank, base_result(row))

    if skill == "Speed Burst":
        if speed_bonus and maximum is not None:
            return result(maximum, "C Rank with full speed bonus", "SRankMAX")
        if rank_at_least(rank, "C") and conditional is not None:
            return apply_verso_rank_bonus(rank, result(conditional, "C Rank", "ConDmg"))
        return apply_verso_rank_bonus(rank, base_result(row))

    if rank == "S" and maximum is not None and skill not in {"Ranged Attack", "Basic Attack", "Counter"}:
        return result(maximum, "S Rank", "SRankMAX")

    if rank_at_least(rank, required_rank) and conditional is not None:
        return apply_verso_rank_bonus(rank, result(conditional, f"{required_rank} Rank", "ConDmg"))

    return apply_verso_rank_bonus(rank, base_result(row))


CALCULATORS = {
    "gustave": calculate_gustave,
    "lune": calculate_lune,
    "maelle": calculate_maelle,
    "monoco": calculate_monoco,
    "sciel": calculate_sciel,
    "verso": calculate_verso,
}


def calculate_skill_result(
    character: str,
    row: CalculatorRow,
    state: CalculatorState,
) -> CalculationResult:
    """Dispatch skill calculation to the character-specific calculator."""

    return CALCULATORS[character](row, state)


def resolve_picto_attack_type(row: CalculatorRow, override: str | None) -> str:
    """Resolve the attack type used by attack-specific Picto bonuses."""

    if override and override != "Auto":
        return override

    skill = clean_text(row.get("Skill")).lower()
    if skill == "basic attack":
        return "Base Attack"
    if skill == "counter":
        return "Counterattack"
    if skill == "ranged attack":
        return "Free Aim"
    if "gradient attack" in skill:
        return "Gradient Attack"
    return "Skill"


def apply_picto_bonus(skill_result: CalculationResult, picto_summary: PictoSummary) -> CalculationResult:
    """Apply the combined Picto multiplier to the calculated skill result."""

    multiplier = skill_result.get("multiplier")
    total_factor = picto_summary["total_factor"]
    if multiplier is None or not picto_summary["active"] or total_factor == 1:
        return skill_result

    return result(
        round(multiplier * total_factor, 2),
        skill_result["scenario"],
        f"{skill_result['source']} + Pictos",
        skill_result.get("warning"),
    )


def build_skill_control_styles(character: str, row: CalculatorRow) -> ControlStyles:
    """Return per-control visibility styles for the selected character skill."""

    skill = clean_text(row.get("Skill"))
    condition = text_from_row(row, "Condition 1", "Condition").lower()
    max_condition = text_from_row(row, "Con Max Dmg", "ConTwilight").lower()
    styles: ControlStyles = {}

    def set_visibility(control: str, is_visible: bool) -> None:
        styles[control] = VISIBLE_STYLE if is_visible else HIDDEN_STYLE

    if character == "gustave":
        set_visibility("gustave_charges", skill.startswith("Overcharge"))
        return styles

    if character == "lune":
        set_visibility("lune_stains", "stain" in condition or "stain" in max_condition or skill in {"Storm Caller"})
        set_visibility(
            "lune_turns",
            skill.startswith("Burn ")
            or condition == "turn start dmg"
            or skill in {"Fire Rage", "Fire Rage Stained", "Storm Caller"},
        )
        set_visibility("lune_all_crits", "crit" in max_condition)
        return styles

    if character == "maelle":
        set_visibility("maelle_stance", not skill.startswith("Burn "))
        set_visibility("maelle_burn_stacks", skill in {"Burning Canvas", "Combustion"})
        set_visibility("maelle_hits_taken", skill == "Revenge")
        set_visibility("maelle_marked", skill in {"G-Homage", "Momentum Strike", "Percee"})
        set_visibility("maelle_all_crits", skill == "Sword Ballet")
        return styles

    if character == "monoco":
        set_visibility("monoco_turns", skill.startswith("Burn ") or skill in {"Sakapate Fire", "Abberation Light", "Braseleur Smash"})
        set_visibility("monoco_mask", uses_mask_condition(row) or can_apply_generic_monoco_mask_bonus(row))
        set_visibility("monoco_stunned", skill in {"Mighty Strike", "Sakapate Estoc"})
        set_visibility("monoco_marked", skill == "Sakapate Slam")
        set_visibility("monoco_powerless", skill == "Obscur Sword")
        set_visibility("monoco_burning", skill == "Danseuse Waltz")
        set_visibility("monoco_low_life", skill == "Cultist Slashes")
        set_visibility("monoco_full_life", skill == "Cultist Blood")
        set_visibility("monoco_all_crits", skill in {"Chevalier Thrusts", "Sakapate Explosion"})
        return styles

    if character == "sciel":
        set_visibility("sciel_foretell", skill in SCIEL_FORETELL_RATES or skill in {"Our Sacrifice", "Sealed Fate", "Firing Shadow"})
        set_visibility("sciel_twilight", number_from_row(row, "TwilightDmg") is not None)
        set_visibility("sciel_full_life", skill == "Our Sacrifice")
        return styles

    if character == "verso":
        set_visibility(
            "verso_rank",
            skill not in {"Ranged Attack", "Basic Attack", "Counter"}
            and (
                parse_rank_requirement(text_from_row(row, "Condition")) is not None
                or number_from_row(row, "SRankMAX") is not None
                or skill in {"Follow Up", "Ascending Assault", "Speed Burst", "End Bringer", "Steeled Strike"}
            ),
        )
        set_visibility("verso_shots", skill == "Follow Up")
        set_visibility("verso_uses", skill in {"Steeled Strike", "Ascending Assault"})
        set_visibility("verso_stunned", skill == "End Bringer")
        set_visibility("verso_speed_bonus", skill == "Speed Burst")
        return styles

    return styles
