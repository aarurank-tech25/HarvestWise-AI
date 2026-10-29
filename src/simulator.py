"""
HarvestWise AI — Core Simulation Engine
Calculates spoilage, sellable quantity, gross revenue, operating costs, and net farmer value
across three distinct options without double-counting costs.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from src.validation import validate_simulation_inputs


WEATHER_MULTIPLIERS = {
    "Low": 0.85,
    "Moderate": 1.00,
    "High": 1.35
}

STORAGE_MULTIPLIERS = {
    "Good": 0.70,
    "Average": 1.00,
    "Poor": 1.40
}


@dataclass
class OptionResult:
    option_key: str
    option_name: str
    spoilage_pct: float
    sellable_kg: float
    gross_revenue: float
    storage_cost: float
    transport_cost: float
    total_operating_cost: float
    net_farmer_value: float
    unit_net_value: float  # ₹ per original kg


@dataclass
class SimulationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    inputs: Dict[str, Any]
    
    # Baseline
    baseline_gross_revenue: float
    baseline_operating_cost: float
    baseline_net_value: float
    
    # Options
    options: Dict[str, OptionResult]
    
    # Decision
    recommended_option_key: str
    recommended_option_name: str
    recommended_net_value: float
    recommendation_reason: str
    tipping_points: List[str]
    is_immature: bool
    is_tie: bool


def calculate_effective_spoilage(
    base_spoilage_pct: float,
    weather_risk: str,
    storage_quality: str,
    transport_hours: float,
    transit_penalty_per_hour: float = 0.015,
    additional_decay_pct: float = 0.0
) -> float:
    """
    Computes effective spoilage rate bounded between 0% and 98%.
    Formula:
        base_rate = base_spoilage_pct / 100
        env_factor = weather_mult * storage_mult
        transit_factor = 1.0 + max(0, transport_hours - 1) * transit_penalty
        spoilage = (base_rate * env_factor * transit_factor) + (additional_decay / 100)
    """
    base_rate = max(0.0, base_spoilage_pct) / 100.0
    w_mult = WEATHER_MULTIPLIERS.get(weather_risk, 1.0)
    s_mult = STORAGE_MULTIPLIERS.get(storage_quality, 1.0)
    transit_factor = 1.0 + max(0.0, transport_hours - 1.0) * transit_penalty_per_hour
    
    effective = (base_rate * w_mult * s_mult * transit_factor) + (additional_decay_pct / 100.0)
    return min(98.0, max(0.0, effective * 100.0))


def run_simulation(inputs: Dict[str, Any]) -> SimulationResult:
    """
    Executes complete multi-option harvest & market simulation.
    Ensures zero cost double-counting:
      - Option 1 (Harvest Now): Storage cost = ₹0, Transport cost = Nearby transport
      - Option 2 (Wait): Storage cost = Qty * Days * Cost/kg/day, Transport = Nearby transport
      - Option 3 (Alternate Market): Storage cost = ₹0, Transport = Alternate transport
    """
    is_valid, errors, warnings = validate_simulation_inputs(inputs)
    
    if not is_valid:
        return SimulationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            inputs=inputs,
            baseline_gross_revenue=0.0,
            baseline_operating_cost=0.0,
            baseline_net_value=0.0,
            options={},
            recommended_option_key="none",
            recommended_option_name="Invalid Inputs",
            recommended_net_value=0.0,
            recommendation_reason="Simulation halted due to input errors.",
            tipping_points=[],
            is_immature=False,
            is_tie=False
        )

    # Extract validated variables
    q = float(inputs["quantity_kg"])
    maturity = float(inputs["maturity_pct"])
    cp = float(inputs["current_price"])
    fp = float(inputs["future_price"])
    ap = float(inputs.get("alt_price", cp))
    base_sp = float(inputs["base_spoilage_pct"])
    wait_d = int(inputs["wait_days"])
    sc_rate = float(inputs["storage_cost_per_kg_day"])
    tc_near = float(inputs["transport_cost_nearby"])
    th_near = float(inputs["transport_hours_nearby"])
    tc_alt = float(inputs["transport_cost_alt"])
    th_alt = float(inputs["transport_hours_alt"])
    weather = inputs["weather_risk"]
    storage = inputs["storage_quality"]
    
    # -------------------------------------------------------------
    # 1. Naive Baseline (ignores spoilage, ignores storage costs)
    # -------------------------------------------------------------
    baseline_gross = q * cp
    baseline_op_cost = tc_near
    baseline_net = baseline_gross - baseline_op_cost

    # -------------------------------------------------------------
    # 2. Option 1: Harvest Now (Nearby Market)
    # -------------------------------------------------------------
    sp_now = calculate_effective_spoilage(
        base_spoilage_pct=base_sp,
        weather_risk=weather,
        storage_quality=storage,
        transport_hours=th_near,
        transit_penalty_per_hour=0.012
    )
    sellable_now = q * (1.0 - (sp_now / 100.0))
    gross_now = sellable_now * cp
    storage_now = 0.0  # Zero storage cost for immediate harvest & sale
    trans_now = tc_near
    cost_now = storage_now + trans_now
    net_now = gross_now - cost_now
    unit_net_now = net_now / q if q > 0 else 0.0

    opt_now = OptionResult(
        option_key="harvest_now",
        option_name="Harvest Now (Nearby Market)",
        spoilage_pct=sp_now,
        sellable_kg=sellable_now,
        gross_revenue=gross_now,
        storage_cost=storage_now,
        transport_cost=trans_now,
        total_operating_cost=cost_now,
        net_farmer_value=net_now,
        unit_net_value=unit_net_now
    )

    # -------------------------------------------------------------
    # 3. Option 2: Wait for Better Price (Nearby Market after N days)
    # -------------------------------------------------------------
    w_mult = WEATHER_MULTIPLIERS.get(weather, 1.0)
    s_mult = STORAGE_MULTIPLIERS.get(storage, 1.0)
    # Daily waiting decay rate modulated by weather and storage quality
    daily_decay = 1.2 * w_mult * s_mult
    additional_wait_decay = wait_d * daily_decay
    
    sp_wait = calculate_effective_spoilage(
        base_spoilage_pct=base_sp,
        weather_risk=weather,
        storage_quality=storage,
        transport_hours=th_near,
        transit_penalty_per_hour=0.012,
        additional_decay_pct=additional_wait_decay
    )
    sellable_wait = q * (1.0 - (sp_wait / 100.0))
    gross_wait = sellable_wait * fp
    storage_wait = q * wait_d * sc_rate
    trans_wait = tc_near
    cost_wait = storage_wait + trans_wait
    net_wait = gross_wait - cost_wait
    unit_net_wait = net_wait / q if q > 0 else 0.0

    opt_wait = OptionResult(
        option_key="wait_price",
        option_name="Wait for Better Price",
        spoilage_pct=sp_wait,
        sellable_kg=sellable_wait,
        gross_revenue=gross_wait,
        storage_cost=storage_wait,
        transport_cost=trans_wait,
        total_operating_cost=cost_wait,
        net_farmer_value=net_wait,
        unit_net_value=unit_net_wait
    )

    # -------------------------------------------------------------
    # 4. Option 3: Alternate / Distant Market
    # -------------------------------------------------------------
    sp_alt = calculate_effective_spoilage(
        base_spoilage_pct=base_sp,
        weather_risk=weather,
        storage_quality=storage,
        transport_hours=th_alt,
        transit_penalty_per_hour=0.020  # higher transit vibration penalty for long routes
    )
    sellable_alt = q * (1.0 - (sp_alt / 100.0))
    gross_alt = sellable_alt * ap
    storage_alt = 0.0  # Zero storage cost for direct dispatch
    trans_alt = tc_alt
    cost_alt = storage_alt + trans_alt
    net_alt = gross_alt - cost_alt
    unit_net_alt = net_alt / q if q > 0 else 0.0

    opt_alt = OptionResult(
        option_key="alt_market",
        option_name="Alternate / Distant Market",
        spoilage_pct=sp_alt,
        sellable_kg=sellable_alt,
        gross_revenue=gross_alt,
        storage_cost=storage_alt,
        transport_cost=trans_alt,
        total_operating_cost=cost_alt,
        net_farmer_value=net_alt,
        unit_net_value=unit_net_alt
    )

    options_dict = {
        "harvest_now": opt_now,
        "wait_price": opt_wait,
        "alt_market": opt_alt
    }

    # -------------------------------------------------------------
    # 5. Recommendation Engine & Tie-Breaking
    # -------------------------------------------------------------
    is_immature = maturity < 65.0
    sorted_options = sorted(options_dict.values(), key=lambda o: o.net_farmer_value, reverse=True)
    best_opt = sorted_options[0]
    second_opt = sorted_options[1]
    
    # Tie check (difference less than ₹50 on total or ₹0.05/kg)
    diff = abs(best_opt.net_farmer_value - second_opt.net_farmer_value)
    is_tie = diff <= 50.0

    # Tie-breaking priority based on risk: Harvest Now (least risk) > Alternate > Wait
    if is_tie:
        risk_priority = ["harvest_now", "alt_market", "wait_price"]
        tie_candidates = [best_opt, second_opt]
        best_opt = min(tie_candidates, key=lambda o: risk_priority.index(o.option_key))

    # Construct decision explanation & tipping points
    tipping_points = []
    
    # Tipping point 1: Future price break-even with Harvest Now
    # gross_wait - cost_wait = net_now => sellable_wait * fp - cost_wait = net_now
    # => fp_breakeven = (net_now + cost_wait) / sellable_wait
    if sellable_wait > 0:
        fp_breakeven = (net_now + cost_wait) / sellable_wait
        tipping_points.append(
            f"Future Price Tipping Point: Waiting matches immediate harvest if future price reaches ₹{fp_breakeven:.2f}/kg "
            f"(current expectation: ₹{fp:.2f}/kg)."
        )

    # Tipping point 2: Alternate price break-even with Harvest Now
    if sellable_alt > 0:
        ap_breakeven = (net_now + cost_alt) / sellable_alt
        tipping_points.append(
            f"Alternate Market Tipping Point: Alternate market matches immediate harvest if price reaches ₹{ap_breakeven:.2f}/kg "
            f"(current assumption: ₹{ap:.2f}/kg)."
        )

    # Tipping point 3: Spoilage threshold for waiting
    # If waiting spoilage increases by more than X%
    if fp > 0 and q > 0:
        max_tolerable_spoilage = max(0.0, 1.0 - ((net_now + cost_wait) / (q * fp))) * 100.0
        tipping_points.append(
            f"Spoilage Tolerance: If waiting spoilage climbs above {max_tolerable_spoilage:.1f}%, Waiting will yield less than Harvesting Now."
        )

    if is_immature:
        rec_key = "immature_hold"
        rec_name = "Hold / Confirm Maturity"
        rec_reason = (
            f"Crop maturity is only {maturity:.1f}% (< 65% benchmark). "
            f"Harvesting now is premature and risks substantial market price deductions or high in-transit rot. "
            f"Verify physical indicators (color, firm texture) with local extension experts before cutting."
        )
    else:
        rec_key = best_opt.option_key
        rec_name = best_opt.option_name
        
        if rec_key == "harvest_now":
            rec_reason = (
                f"Immediate harvest secures ₹{net_now:,.0f} net farmer value, avoiding ₹{storage_wait:,.0f} in storage costs "
                f"and eliminating weather-induced decay risks. Compared to naive baseline (₹{baseline_net:,.0f}), "
                f"this accounts for realistic {sp_now:.1f}% field/transit spoilage."
            )
        elif rec_key == "wait_price":
            net_gain_vs_now = net_wait - net_now
            rec_reason = (
                f"Waiting {wait_d} days generates the highest net return of ₹{net_wait:,.0f} "
                f"(+₹{net_gain_vs_now:,.0f} compared to immediate harvest). The expected price rise of +₹{fp - cp:.2f}/kg "
                f"sufficiently absorbs ₹{storage_wait:,.0f} in storage costs and {sp_wait - sp_now:.1f}% added spoilage loss."
            )
        else:  # alt_market
            net_gain_vs_now = net_alt - net_now
            rec_reason = (
                f"Dispatching produce to {inputs.get('alt_market_name', 'Alternate Market')} yields ₹{net_alt:,.0f} "
                f"(+₹{net_gain_vs_now:,.0f} advantage over nearby market). The premium price of ₹{ap:.2f}/kg overcomes "
                f"the higher transport expense (₹{tc_alt:,.0f}) and transit decay."
            )

        if is_tie:
            rec_reason += f" [Note: Return is within ₹{diff:.0f} of runner-up; recommended option carries lower operational risk.]"

    return SimulationResult(
        is_valid=True,
        errors=[],
        warnings=warnings,
        inputs=inputs,
        baseline_gross_revenue=baseline_gross,
        baseline_operating_cost=baseline_op_cost,
        baseline_net_value=baseline_net,
        options=options_dict,
        recommended_option_key=rec_key,
        recommended_option_name=rec_name,
        recommended_net_value=best_opt.net_farmer_value,
        recommendation_reason=rec_reason,
        tipping_points=tipping_points,
        is_immature=is_immature,
        is_tie=is_tie
    )
