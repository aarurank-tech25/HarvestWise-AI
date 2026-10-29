"""
HarvestWise AI — Reproducible Scenarios Module
Defines Scenarios A, B, and C with full baseline comparisons and audit logs.
"""

from typing import Dict, Any, List
import pandas as pd
from src.simulator import run_simulation, SimulationResult


REPRODUCIBLE_SCENARIOS = {
    "A": {
        "id": "A",
        "name": "Scenario A: Mature Crop with Stable Weather & Nearby Market",
        "crop_name": "Tomato",
        "quantity_kg": 1000.0,
        "maturity_pct": 92.0,
        "current_price": 30.0,
        "future_price": 30.0,
        "alt_price": 30.0,
        "base_spoilage_pct": 4.0,
        "wait_days": 1,
        "storage_cost_per_kg_day": 0.20,
        "transport_cost_nearby": 1200.0,
        "transport_hours_nearby": 1.0,
        "transport_cost_alt": 3500.0,
        "transport_hours_alt": 6.0,
        "weather_risk": "Low",
        "storage_quality": "Good",
        "market_nearby_name": "Local Taluk Mandi",
        "market_alt_name": "Distant District Yard",
        "hypothesis": "With mature crop, low weather risk, and minimal price gain (+₹1/kg), immediate harvest minimizes holding losses."
    },
    "B": {
        "id": "B",
        "name": "Scenario B: Price Rise with Rainy Weather & Waiting Storage Costs",
        "crop_name": "Tomato",
        "quantity_kg": 1000.0,
        "maturity_pct": 88.0,
        "current_price": 24.0,
        "future_price": 35.0,
        "alt_price": 25.0,
        "base_spoilage_pct": 8.0,
        "wait_days": 4,
        "storage_cost_per_kg_day": 0.35,
        "transport_cost_nearby": 1400.0,
        "transport_hours_nearby": 2.0,
        "transport_cost_alt": 4000.0,
        "transport_hours_alt": 8.0,
        "weather_risk": "High",
        "storage_quality": "Average",
        "market_nearby_name": "Town Primary Yard",
        "market_alt_name": "Regional Hub Mandi",
        "hypothesis": "Tests if a substantial price increase (+₹11/kg) overcomes wet-weather decay acceleration and 4 days of storage expense."
    },
    "C": {
        "id": "C",
        "name": "Scenario C: Higher-Price Alternate Market with Longer Transport",
        "crop_name": "Tomato",
        "quantity_kg": 1000.0,
        "maturity_pct": 95.0,
        "current_price": 25.0,
        "future_price": 26.0,
        "alt_price": 36.0,
        "base_spoilage_pct": 5.0,
        "wait_days": 0,
        "storage_cost_per_kg_day": 0.20,
        "transport_cost_nearby": 1200.0,
        "transport_hours_nearby": 1.5,
        "transport_cost_alt": 3800.0,
        "transport_hours_alt": 7.0,
        "weather_risk": "Moderate",
        "storage_quality": "Good",
        "market_nearby_name": "Local Regulated Market",
        "market_alt_name": "Capital Wholesale APMC",
        "hypothesis": "Tests spatial price arbitrage: whether a +₹11/kg price premium at a distant market offsets ₹3,800 freight and transit spoilage."
    }
}


def get_scenario(scenario_id: str) -> Dict[str, Any]:
    """Retrieve raw parameter dictionary for a scenario."""
    return REPRODUCIBLE_SCENARIOS.get(scenario_id, REPRODUCIBLE_SCENARIOS["A"]).copy()


def run_all_scenarios() -> Dict[str, SimulationResult]:
    """Execute all three core scenarios and return dictionary of results."""
    results = {}
    for key, sc_data in REPRODUCIBLE_SCENARIOS.items():
        results[key] = run_simulation(sc_data)
    return results


def build_scenario_comparison_df(results: Dict[str, SimulationResult]) -> pd.DataFrame:
    """
    Constructs comprehensive tabular comparison showing:
    - Baseline value (naive)
    - Effective spoilage for each option
    - Net farmer value for each option
    - Selected recommendation
    - Realistic value gain/loss vs naive baseline
    """
    rows = []
    for sc_id, sim in results.items():
        if not sim.is_valid:
            continue
        sc_info = REPRODUCIBLE_SCENARIOS[sc_id]
        
        opt_now = sim.options["harvest_now"]
        opt_wait = sim.options["wait_price"]
        opt_alt = sim.options["alt_market"]
        
        # Calculate naive baseline error
        # Naive baseline claims farmer gets baseline_net_value, but real net_now is lower due to spoilage!
        baseline_overestimation = sim.baseline_net_value - opt_now.net_farmer_value
        
        rows.append({
            "Scenario ID": sc_id,
            "Scenario Name": sc_info["name"].split(":")[1].strip(),
            "Crop": sc_info["crop_name"],
            "Qty (kg)": sc_info["quantity_kg"],
            "Weather": sc_info["weather_risk"],
            "Naive Baseline (₹)": round(sim.baseline_net_value, 0),
            "Harvest Now Net (₹)": round(opt_now.net_farmer_value, 0),
            "Wait Net (₹)": round(opt_wait.net_farmer_value, 0),
            "Alt Market Net (₹)": round(opt_alt.net_farmer_value, 0),
            "Spoilage Now (%)": round(opt_now.spoilage_pct, 1),
            "Spoilage Wait (%)": round(opt_wait.spoilage_pct, 1),
            "Spoilage Alt (%)": round(opt_alt.spoilage_pct, 1),
            "Recommended Decision": sim.recommended_option_name,
            "Max Net Value (₹)": round(sim.recommended_net_value, 0),
            "Naive Baseline Error (₹)": round(baseline_overestimation, 0)
        })
    return pd.DataFrame(rows)
