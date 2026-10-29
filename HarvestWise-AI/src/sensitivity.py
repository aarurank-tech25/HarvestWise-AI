"""
HarvestWise AI — Sensitivity Analysis Engine
Performs parametric sweeps across future price, spoilage, weather, storage costs,
transport time, and waiting period to pinpoint critical decision boundary flips.
"""

from typing import Dict, Any, List, Tuple
import pandas as pd
from src.simulator import run_simulation


def sweep_variable(
    base_inputs: Dict[str, Any],
    variable_key: str,
    values: List[Any],
    display_name: str
) -> pd.DataFrame:
    """
    Executes parametric sweep for a specific parameter while holding other assumptions constant.
    Tracks net returns and flags crossover decision shifts.
    """
    rows = []
    previous_best = None
    
    for val in values:
        test_inputs = base_inputs.copy()
        test_inputs[variable_key] = val
        
        sim = run_simulation(test_inputs)
        if not sim.is_valid:
            continue
            
        opt_now = sim.options["harvest_now"]
        opt_wait = sim.options["wait_price"]
        opt_alt = sim.options["alt_market"]
        
        best_key = sim.recommended_option_key
        best_name = sim.recommended_option_name
        
        crossover_event = ""
        if previous_best is not None and previous_best != best_key:
            crossover_event = f"⚡ FLIP: {previous_best.replace('_', ' ').title()} ➔ {best_key.replace('_', ' ').title()}"
        previous_best = best_key
        
        rows.append({
            display_name: val,
            "Harvest Now (₹)": round(opt_now.net_farmer_value, 1),
            "Wait (₹)": round(opt_wait.net_farmer_value, 1),
            "Alternate Market (₹)": round(opt_alt.net_farmer_value, 1),
            "Recommended Decision": best_name,
            "Decision Flip": crossover_event
        })
        
    return pd.DataFrame(rows)


def analyze_future_price_sensitivity(
    base_inputs: Dict[str, Any],
    min_price: float = 15.0,
    max_price: float = 50.0,
    step: float = 2.5
) -> pd.DataFrame:
    """Sweeps expected future market price."""
    prices = []
    curr = min_price
    while curr <= max_price + 1e-5:
        prices.append(round(curr, 2))
        curr += step
    return sweep_variable(base_inputs, "future_price", prices, "Future Price (₹/kg)")


def analyze_spoilage_sensitivity(
    base_inputs: Dict[str, Any],
    min_sp: float = 0.0,
    max_sp: float = 30.0,
    step: float = 3.0
) -> pd.DataFrame:
    """Sweeps base spoilage percentage."""
    rates = []
    curr = min_sp
    while curr <= max_sp + 1e-5:
        rates.append(round(curr, 1))
        curr += step
    return sweep_variable(base_inputs, "base_spoilage_pct", rates, "Base Spoilage (%)")


def analyze_weather_sensitivity(base_inputs: Dict[str, Any]) -> pd.DataFrame:
    """Evaluates impact across all standard weather categories."""
    weathers = ["Low", "Moderate", "High"]
    return sweep_variable(base_inputs, "weather_risk", weathers, "Weather Condition")


def analyze_storage_cost_sensitivity(
    base_inputs: Dict[str, Any],
    min_cost: float = 0.0,
    max_cost: float = 1.0,
    step: float = 0.10
) -> pd.DataFrame:
    """Sweeps daily storage fees per kg."""
    costs = []
    curr = min_cost
    while curr <= max_cost + 1e-5:
        costs.append(round(curr, 2))
        curr += step
    return sweep_variable(base_inputs, "storage_cost_per_kg_day", costs, "Storage Cost (₹/kg/day)")


def analyze_transport_time_sensitivity(
    base_inputs: Dict[str, Any],
    min_hours: float = 1.0,
    max_hours: float = 15.0,
    step: float = 2.0
) -> pd.DataFrame:
    """Sweeps alternate market transit hours."""
    hours = []
    curr = min_hours
    while curr <= max_hours + 1e-5:
        hours.append(round(curr, 1))
        curr += step
    return sweep_variable(base_inputs, "transport_hours_alt", hours, "Alt Transport Hours")


def analyze_wait_days_sensitivity(
    base_inputs: Dict[str, Any],
    min_days: int = 0,
    max_days: int = 10
) -> pd.DataFrame:
    """Sweeps waiting duration in days."""
    days = list(range(min_days, max_days + 1))
    return sweep_variable(base_inputs, "wait_days", days, "Waiting Duration (Days)")


def find_critical_tipping_points(base_inputs: Dict[str, Any]) -> List[str]:
    """
    Summarizes key crossover thresholds where decisions shift.
    """
    tips = []
    sim = run_simulation(base_inputs)
    if not sim.is_valid:
        return ["Invalid baseline inputs."]
        
    tips.extend(sim.tipping_points)
    
    # Check weather flip
    w_df = analyze_weather_sensitivity(base_inputs)
    decisions = w_df["Recommended Decision"].tolist()
    if len(set(decisions)) > 1:
        tips.append(f"Weather Sensitivity: Decision changes with weather conditions ({' vs '.join(set(decisions))}).")
    else:
        tips.append("Weather Invariance: Decision remains stable across all weather categories with current price spreads.")
        
    return tips
