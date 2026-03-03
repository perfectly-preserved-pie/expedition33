from __future__ import annotations
from dash import Input, Output, callback
from typing import Any
from games.expedition33.calculator.core import (
    calculate_current_cost,
    CALCULATOR_DATA,
    CharacterStyles,
    ComponentChildren,
    ControlStyles,
    DEFAULT_CHARACTER,
    DEFAULT_SKILLS,
    get_row,
    HIDDEN_STYLE,
    NumericInput,
    parse_number,
    skill_options_for,
    SkillOption,
    StyleRule,
    ToggleInput,
    VISIBLE_STYLE,
)
from games.expedition33.calculator.layout import build_result_body, build_summary_body
from games.expedition33.calculator.logic import (
    apply_picto_bonus,
    build_skill_control_styles,
    calculate_skill_result,
    resolve_picto_attack_type,
)
from games.expedition33.calculator.pictos import evaluate_pictos, required_picto_controls

def build_character_section_styles(active_character: str) -> tuple[list[str], CharacterStyles]:
    """Return accordion visibility styles for the active character."""

    active_item = [f"setup-{active_character}"]
    styles = {
        character: VISIBLE_STYLE if character == active_character else HIDDEN_STYLE
        for character in CALCULATOR_DATA
    }
    return active_item, styles


def control_style(control_styles: ControlStyles, control: str) -> StyleRule:
    """Return the style for a single control wrapper."""

    return control_styles.get(control, HIDDEN_STYLE)


def empty_state_style(control_styles: ControlStyles, prefix: str) -> StyleRule:
    """Show the placeholder when no controls are visible for the section."""

    has_visible_control = any(
        key.startswith(prefix) and value == VISIBLE_STYLE
        for key, value in control_styles.items()
    )
    return HIDDEN_STYLE if has_visible_control else VISIBLE_STYLE


def build_calculator_states(
    gustave_charges: NumericInput,
    lune_stains: NumericInput,
    lune_turns: NumericInput,
    lune_all_crits: ToggleInput,
    maelle_stance: str | None,
    maelle_burn_stacks: NumericInput,
    maelle_hits_taken: NumericInput,
    maelle_marked: ToggleInput,
    maelle_all_crits: ToggleInput,
    monoco_turns: NumericInput,
    monoco_mask: ToggleInput,
    monoco_stunned: ToggleInput,
    monoco_marked: ToggleInput,
    monoco_powerless: ToggleInput,
    monoco_burning: ToggleInput,
    monoco_low_life: ToggleInput,
    monoco_full_life: ToggleInput,
    monoco_all_crits: ToggleInput,
    sciel_foretell: NumericInput,
    sciel_twilight: ToggleInput,
    sciel_full_life: ToggleInput,
    verso_rank: str | None,
    verso_shots: NumericInput,
    verso_uses: NumericInput,
    verso_stunned: ToggleInput,
    verso_speed_bonus: ToggleInput,
) -> dict[str, dict[str, Any]]:
    """Normalize callback inputs into per-character calculator state."""

    return {
        "gustave": {
            "charges": gustave_charges,
        },
        "lune": {
            "stains": lune_stains,
            "turns": lune_turns,
            "all_crits": lune_all_crits,
        },
        "maelle": {
            "stance": maelle_stance,
            "burn_stacks": maelle_burn_stacks,
            "hits_taken": maelle_hits_taken,
            "marked": maelle_marked,
            "all_crits": maelle_all_crits,
            "turns": 3,
        },
        "monoco": {
            "turns": monoco_turns,
            "mask_active": monoco_mask,
            "stunned": monoco_stunned,
            "marked": monoco_marked,
            "powerless": monoco_powerless,
            "burning": monoco_burning,
            "low_life": monoco_low_life,
            "full_life": monoco_full_life,
            "all_crits": monoco_all_crits,
        },
        "sciel": {
            "foretell": sciel_foretell,
            "twilight": sciel_twilight,
            "full_life": sciel_full_life,
        },
        "verso": {
            "rank": verso_rank,
            "shots": verso_shots,
            "uses": verso_uses,
            "stunned": verso_stunned,
            "speed_bonus": verso_speed_bonus,
        },
    }


def build_picto_state(
    resolved_attack_type: str,
    picto_below_10_health: ToggleInput,
    picto_target_burning: ToggleInput,
    picto_target_stunned: ToggleInput,
    picto_exhausted: ToggleInput,
    picto_full_health: ToggleInput,
    picto_unhit: ToggleInput,
    picto_inverted: ToggleInput,
    picto_consume_ap: ToggleInput,
    picto_shield_points: NumericInput,
    picto_fighting_alone: ToggleInput,
    picto_all_allies_alive: ToggleInput,
    picto_status_effects: NumericInput,
    picto_dodge_stacks: NumericInput,
    picto_parry_stacks: NumericInput,
    picto_warming_up_stacks: NumericInput,
    picto_first_hit: ToggleInput,
) -> dict[str, Any]:
    """Normalize callback inputs into a Picto evaluation state."""

    return {
        "attack_type": resolved_attack_type,
        "below_10_health": picto_below_10_health,
        "target_burning": picto_target_burning,
        "target_stunned": picto_target_stunned,
        "exhausted": picto_exhausted,
        "full_health": picto_full_health,
        "unhit": picto_unhit,
        "inverted": picto_inverted,
        "consume_ap": picto_consume_ap,
        "shield_points": picto_shield_points,
        "fighting_alone": picto_fighting_alone,
        "all_allies_alive": picto_all_allies_alive,
        "status_effects": picto_status_effects,
        "dodge_stacks": picto_dodge_stacks,
        "parry_stacks": picto_parry_stacks,
        "warming_up_stacks": picto_warming_up_stacks,
        "first_hit": picto_first_hit,
    }


@callback(
    Output("exp33-calculator-skill", "options"),
    Output("exp33-calculator-skill", "value"),
    Output("exp33-calculator-attack", "value"),
    Input("exp33-calculator-character", "value"),
)
def update_skill_dropdown(character: str | None) -> tuple[list[SkillOption], str, float]:
    """Refresh the skill dropdown and default attack when the character changes."""

    selected_character = character or DEFAULT_CHARACTER
    options = skill_options_for(selected_character)
    default_skill = DEFAULT_SKILLS.get(selected_character, options[0]["value"])
    if default_skill not in {option["value"] for option in options}:
        default_skill = options[0]["value"]
    attack = CALCULATOR_DATA[selected_character]["default_attack"]
    return options, default_skill, attack


@callback(
    Output("exp33-calculator-character-accordion", "active_item"),
    Output("exp33-calculator-item-gustave", "style"),
    Output("exp33-calculator-item-lune", "style"),
    Output("exp33-calculator-item-maelle", "style"),
    Output("exp33-calculator-item-monoco", "style"),
    Output("exp33-calculator-item-sciel", "style"),
    Output("exp33-calculator-item-verso", "style"),
    Output("exp33-calculator-control-gustave-charges", "style"),
    Output("exp33-calculator-control-lune-stains", "style"),
    Output("exp33-calculator-control-lune-turns", "style"),
    Output("exp33-calculator-control-lune-all-crits", "style"),
    Output("exp33-calculator-control-maelle-stance", "style"),
    Output("exp33-calculator-control-maelle-burn-stacks", "style"),
    Output("exp33-calculator-control-maelle-hits-taken", "style"),
    Output("exp33-calculator-control-maelle-marked", "style"),
    Output("exp33-calculator-control-maelle-all-crits", "style"),
    Output("exp33-calculator-control-monoco-turns", "style"),
    Output("exp33-calculator-control-monoco-mask", "style"),
    Output("exp33-calculator-control-monoco-stunned", "style"),
    Output("exp33-calculator-control-monoco-marked", "style"),
    Output("exp33-calculator-control-monoco-powerless", "style"),
    Output("exp33-calculator-control-monoco-burning", "style"),
    Output("exp33-calculator-control-monoco-low-life", "style"),
    Output("exp33-calculator-control-monoco-full-life", "style"),
    Output("exp33-calculator-control-monoco-all-crits", "style"),
    Output("exp33-calculator-empty-gustave", "style"),
    Output("exp33-calculator-empty-lune", "style"),
    Output("exp33-calculator-empty-maelle", "style"),
    Output("exp33-calculator-empty-monoco", "style"),
    Output("exp33-calculator-empty-sciel", "style"),
    Output("exp33-calculator-empty-verso", "style"),
    Output("exp33-calculator-control-sciel-foretell", "style"),
    Output("exp33-calculator-control-sciel-twilight", "style"),
    Output("exp33-calculator-control-sciel-full-life", "style"),
    Output("exp33-calculator-control-verso-rank", "style"),
    Output("exp33-calculator-control-verso-shots", "style"),
    Output("exp33-calculator-control-verso-uses", "style"),
    Output("exp33-calculator-control-verso-stunned", "style"),
    Output("exp33-calculator-control-verso-speed-bonus", "style"),
    Input("exp33-calculator-character", "value"),
    Input("exp33-calculator-skill", "value"),
)
def sync_visible_controls(character: str | None, skill: str | None) -> tuple[Any, ...]:
    """Show only the control section relevant to the selected character."""

    active_character = character or DEFAULT_CHARACTER
    active_item, styles = build_character_section_styles(active_character)
    row = get_row(active_character, skill)
    control_styles = build_skill_control_styles(active_character, row)

    return (
        active_item,
        styles["gustave"],
        styles["lune"],
        styles["maelle"],
        styles["monoco"],
        styles["sciel"],
        styles["verso"],
        control_style(control_styles, "gustave_charges"),
        control_style(control_styles, "lune_stains"),
        control_style(control_styles, "lune_turns"),
        control_style(control_styles, "lune_all_crits"),
        control_style(control_styles, "maelle_stance"),
        control_style(control_styles, "maelle_burn_stacks"),
        control_style(control_styles, "maelle_hits_taken"),
        control_style(control_styles, "maelle_marked"),
        control_style(control_styles, "maelle_all_crits"),
        control_style(control_styles, "monoco_turns"),
        control_style(control_styles, "monoco_mask"),
        control_style(control_styles, "monoco_stunned"),
        control_style(control_styles, "monoco_marked"),
        control_style(control_styles, "monoco_powerless"),
        control_style(control_styles, "monoco_burning"),
        control_style(control_styles, "monoco_low_life"),
        control_style(control_styles, "monoco_full_life"),
        control_style(control_styles, "monoco_all_crits"),
        empty_state_style(control_styles, "gustave"),
        empty_state_style(control_styles, "lune"),
        empty_state_style(control_styles, "maelle"),
        empty_state_style(control_styles, "monoco"),
        empty_state_style(control_styles, "sciel"),
        empty_state_style(control_styles, "verso"),
        control_style(control_styles, "sciel_foretell"),
        control_style(control_styles, "sciel_twilight"),
        control_style(control_styles, "sciel_full_life"),
        control_style(control_styles, "verso_rank"),
        control_style(control_styles, "verso_shots"),
        control_style(control_styles, "verso_uses"),
        control_style(control_styles, "verso_stunned"),
        control_style(control_styles, "verso_speed_bonus"),
    )


@callback(
    Output("exp33-calculator-pictos-collapse", "is_open"),
    Output("exp33-calculator-picto-control-attack-type", "style"),
    Output("exp33-calculator-picto-control-below-10-health", "style"),
    Output("exp33-calculator-picto-control-target-burning", "style"),
    Output("exp33-calculator-picto-control-target-stunned", "style"),
    Output("exp33-calculator-picto-control-exhausted", "style"),
    Output("exp33-calculator-picto-control-full-health", "style"),
    Output("exp33-calculator-picto-control-unhit", "style"),
    Output("exp33-calculator-picto-control-inverted", "style"),
    Output("exp33-calculator-picto-control-consume-ap", "style"),
    Output("exp33-calculator-picto-control-shield-points", "style"),
    Output("exp33-calculator-picto-control-fighting-alone", "style"),
    Output("exp33-calculator-picto-control-all-allies-alive", "style"),
    Output("exp33-calculator-picto-control-status-effects", "style"),
    Output("exp33-calculator-picto-control-dodge-stacks", "style"),
    Output("exp33-calculator-picto-control-parry-stacks", "style"),
    Output("exp33-calculator-picto-control-warming-up-stacks", "style"),
    Output("exp33-calculator-picto-control-first-hit", "style"),
    Output("exp33-calculator-picto-empty", "style"),
    Input("exp33-calculator-pictos", "value"),
)
def sync_visible_picto_controls(pictos: list[str] | None) -> tuple[Any, ...]:
    """Show only the Picto setup controls required by the selected Pictos."""

    required_controls = required_picto_controls(pictos)
    has_selection = bool(pictos)

    def style_for(control: str) -> StyleRule:
        return VISIBLE_STYLE if control in required_controls else HIDDEN_STYLE

    return (
        has_selection,
        style_for("attack_type"),
        style_for("below_10_health"),
        style_for("target_burning"),
        style_for("target_stunned"),
        style_for("exhausted"),
        style_for("full_health"),
        style_for("unhit"),
        style_for("inverted"),
        style_for("consume_ap"),
        style_for("shield_points"),
        style_for("fighting_alone"),
        style_for("all_allies_alive"),
        style_for("status_effects"),
        style_for("dodge_stacks"),
        style_for("parry_stacks"),
        style_for("warming_up_stacks"),
        style_for("first_hit"),
        VISIBLE_STYLE if has_selection and not required_controls else HIDDEN_STYLE,
    )


@callback(
    Output("exp33-calculator-result-body", "children"),
    Output("exp33-calculator-summary-body", "children"),
    Input("exp33-calculator-character", "value"),
    Input("exp33-calculator-skill", "value"),
    Input("exp33-calculator-attack", "value"),
    Input("exp33-calculator-pictos", "value"),
    Input("exp33-calculator-picto-attack-type", "value"),
    Input("exp33-calculator-picto-below-10-health", "checked"),
    Input("exp33-calculator-picto-target-burning", "checked"),
    Input("exp33-calculator-picto-target-stunned", "checked"),
    Input("exp33-calculator-picto-exhausted", "checked"),
    Input("exp33-calculator-picto-full-health", "checked"),
    Input("exp33-calculator-picto-unhit", "checked"),
    Input("exp33-calculator-picto-inverted", "checked"),
    Input("exp33-calculator-picto-consume-ap", "checked"),
    Input("exp33-calculator-picto-shield-points", "value"),
    Input("exp33-calculator-picto-fighting-alone", "checked"),
    Input("exp33-calculator-picto-all-allies-alive", "checked"),
    Input("exp33-calculator-picto-status-effects", "value"),
    Input("exp33-calculator-picto-dodge-stacks", "value"),
    Input("exp33-calculator-picto-parry-stacks", "value"),
    Input("exp33-calculator-picto-warming-up-stacks", "value"),
    Input("exp33-calculator-picto-first-hit", "checked"),
    Input("exp33-calculator-gustave-charges", "value"),
    Input("exp33-calculator-lune-stains", "value"),
    Input("exp33-calculator-lune-turns", "value"),
    Input("exp33-calculator-lune-all-crits", "checked"),
    Input("exp33-calculator-maelle-stance", "value"),
    Input("exp33-calculator-maelle-burn-stacks", "value"),
    Input("exp33-calculator-maelle-hits-taken", "value"),
    Input("exp33-calculator-maelle-marked", "checked"),
    Input("exp33-calculator-maelle-all-crits", "checked"),
    Input("exp33-calculator-monoco-turns", "value"),
    Input("exp33-calculator-monoco-mask", "checked"),
    Input("exp33-calculator-monoco-stunned", "checked"),
    Input("exp33-calculator-monoco-marked", "checked"),
    Input("exp33-calculator-monoco-powerless", "checked"),
    Input("exp33-calculator-monoco-burning", "checked"),
    Input("exp33-calculator-monoco-low-life", "checked"),
    Input("exp33-calculator-monoco-full-life", "checked"),
    Input("exp33-calculator-monoco-all-crits", "checked"),
    Input("exp33-calculator-sciel-foretell", "value"),
    Input("exp33-calculator-sciel-twilight", "checked"),
    Input("exp33-calculator-sciel-full-life", "checked"),
    Input("exp33-calculator-verso-rank", "value"),
    Input("exp33-calculator-verso-shots", "value"),
    Input("exp33-calculator-verso-uses", "value"),
    Input("exp33-calculator-verso-stunned", "checked"),
    Input("exp33-calculator-verso-speed-bonus", "checked"),
)
def update_calculator_result(
    character: str | None,
    skill: str | None,
    attack: NumericInput,
    pictos: list[str] | None,
    picto_attack_type: str | None,
    picto_below_10_health: ToggleInput,
    picto_target_burning: ToggleInput,
    picto_target_stunned: ToggleInput,
    picto_exhausted: ToggleInput,
    picto_full_health: ToggleInput,
    picto_unhit: ToggleInput,
    picto_inverted: ToggleInput,
    picto_consume_ap: ToggleInput,
    picto_shield_points: NumericInput,
    picto_fighting_alone: ToggleInput,
    picto_all_allies_alive: ToggleInput,
    picto_status_effects: NumericInput,
    picto_dodge_stacks: NumericInput,
    picto_parry_stacks: NumericInput,
    picto_warming_up_stacks: NumericInput,
    picto_first_hit: ToggleInput,
    gustave_charges: NumericInput,
    lune_stains: NumericInput,
    lune_turns: NumericInput,
    lune_all_crits: ToggleInput,
    maelle_stance: str | None,
    maelle_burn_stacks: NumericInput,
    maelle_hits_taken: NumericInput,
    maelle_marked: ToggleInput,
    maelle_all_crits: ToggleInput,
    monoco_turns: NumericInput,
    monoco_mask: ToggleInput,
    monoco_stunned: ToggleInput,
    monoco_marked: ToggleInput,
    monoco_powerless: ToggleInput,
    monoco_burning: ToggleInput,
    monoco_low_life: ToggleInput,
    monoco_full_life: ToggleInput,
    monoco_all_crits: ToggleInput,
    sciel_foretell: NumericInput,
    sciel_twilight: ToggleInput,
    sciel_full_life: ToggleInput,
    verso_rank: str | None,
    verso_shots: NumericInput,
    verso_uses: NumericInput,
    verso_stunned: ToggleInput,
    verso_speed_bonus: ToggleInput,
) -> tuple[ComponentChildren, ComponentChildren]:
    """Recalculate the selected skill and rebuild both result panels."""

    selected_character = character or DEFAULT_CHARACTER
    row = get_row(selected_character, skill)
    attack_value = parse_number(attack) or CALCULATOR_DATA[selected_character]["default_attack"]
    resolved_picto_attack_type = resolve_picto_attack_type(row, picto_attack_type)

    states = build_calculator_states(
        gustave_charges,
        lune_stains,
        lune_turns,
        lune_all_crits,
        maelle_stance,
        maelle_burn_stacks,
        maelle_hits_taken,
        maelle_marked,
        maelle_all_crits,
        monoco_turns,
        monoco_mask,
        monoco_stunned,
        monoco_marked,
        monoco_powerless,
        monoco_burning,
        monoco_low_life,
        monoco_full_life,
        monoco_all_crits,
        sciel_foretell,
        sciel_twilight,
        sciel_full_life,
        verso_rank,
        verso_shots,
        verso_uses,
        verso_stunned,
        verso_speed_bonus,
    )
    picto_state = build_picto_state(
        resolved_picto_attack_type,
        picto_below_10_health,
        picto_target_burning,
        picto_target_stunned,
        picto_exhausted,
        picto_full_health,
        picto_unhit,
        picto_inverted,
        picto_consume_ap,
        picto_shield_points,
        picto_fighting_alone,
        picto_all_allies_alive,
        picto_status_effects,
        picto_dodge_stacks,
        picto_parry_stacks,
        picto_warming_up_stacks,
        picto_first_hit,
    )

    picto_summary = evaluate_pictos(pictos, picto_state)
    skill_result = calculate_skill_result(selected_character, row, states[selected_character])
    skill_result = apply_picto_bonus(skill_result, picto_summary)
    current_cost = calculate_current_cost(selected_character, row, states[selected_character])

    return (
        build_result_body(selected_character, row, attack_value, current_cost, skill_result, picto_summary),
        build_summary_body(row, attack_value, picto_summary["total_factor"]),
    )
