"""
HarvestWise AI — Local Storage & Offline Fallback Module
Handles scenario persistence (JSON/CSV), offline fallback benchmarks,
and explicit data origin provenance (Synthetic vs Manual).
"""

import json
import os
from typing import Dict, Any, List, Optional
import pandas as pd


DATA_ORIGIN_SYNTHETIC = "SYNTHETIC_ACADEMIC_DEMO"
DATA_ORIGIN_MANUAL = "MANUAL_FIELD_OBSERVATION"

# Offline benchmark prices and spoilage rates for fallback when local market information is missing
OFFLINE_REGIONAL_BENCHMARKS = {
    "Tomato": {
        "typical_price_min": 18.0,
        "typical_price_avg": 26.0,
        "typical_price_max": 38.0,
        "base_spoilage_avg": 6.0,
        "max_safe_storage_days": 5,
        "advisory": "Highly perishable; decay accelerates drastically during rain. Avoid storing beyond 4-5 days without refrigeration."
    },
    "Banana": {
        "typical_price_min": 20.0,
        "typical_price_avg": 30.0,
        "typical_price_max": 45.0,
        "base_spoilage_avg": 5.0,
        "max_safe_storage_days": 6,
        "advisory": "Climacteric fruit. Ethylene accumulation in enclosed storage accelerates ripening. Ensure airflow."
    },
    "Mango": {
        "typical_price_min": 40.0,
        "typical_price_avg": 65.0,
        "typical_price_max": 95.0,
        "base_spoilage_avg": 7.0,
        "max_safe_storage_days": 7,
        "advisory": "Vulnerable to anthracnose rot under humid conditions. Sort damaged fruit before packaging."
    },
    "Onion": {
        "typical_price_min": 15.0,
        "typical_price_avg": 24.0,
        "typical_price_max": 40.0,
        "base_spoilage_avg": 3.0,
        "max_safe_storage_days": 45,
        "advisory": "Low perishability if thoroughly cured and kept in well-aerated dry sheds. Keep away from direct ground moisture."
    },
    "Potato": {
        "typical_price_min": 14.0,
        "typical_price_avg": 20.0,
        "typical_price_max": 32.0,
        "base_spoilage_avg": 2.5,
        "max_safe_storage_days": 60,
        "advisory": "Store in darkness to prevent solanine greening. Requires moderate humidity to prevent shrinkage."
    },
    "Green Chili": {
        "typical_price_min": 30.0,
        "typical_price_avg": 48.0,
        "typical_price_max": 75.0,
        "base_spoilage_avg": 8.0,
        "max_safe_storage_days": 4,
        "advisory": "Rapid moisture loss causes wrinkling and mold. Transit in ventilated crates."
    },
    "Paddy / Rice": {
        "typical_price_min": 20.0,
        "typical_price_avg": 25.0,
        "typical_price_max": 32.0,
        "base_spoilage_avg": 1.5,
        "max_safe_storage_days": 180,
        "advisory": "Requires moisture content below 14% before storage to prevent aflatoxin and pest infestation."
    },
    "Other": {
        "typical_price_min": 20.0,
        "typical_price_avg": 30.0,
        "typical_price_max": 50.0,
        "base_spoilage_avg": 5.0,
        "max_safe_storage_days": 7,
        "advisory": "Consult local agricultural extension center for crop-specific post-harvest guidelines."
    }
}


def get_offline_fallback(crop_name: str) -> Dict[str, Any]:
    """Provides regional benchmark values when farmers lack real-time market/weather data."""
    fallback = OFFLINE_REGIONAL_BENCHMARKS.get(crop_name, OFFLINE_REGIONAL_BENCHMARKS["Other"])
    return {
        "crop_name": crop_name,
        "fallback_spot_price": fallback["typical_price_avg"],
        "fallback_future_price": fallback["typical_price_avg"] * 1.05,
        "fallback_spoilage_pct": fallback["base_spoilage_avg"],
        "fallback_weather": "Moderate",  # Conservative offline default
        "fallback_storage": "Average",
        "advisory": fallback["advisory"],
        "provenance": "OFFLINE_REGIONAL_BENCHMARK_RULE_OF_THUMB"
    }


def save_scenario_to_json(scenario_data: Dict[str, Any], filepath: str) -> bool:
    """Saves a scenario dictionary locally as JSON."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def load_scenario_from_json(filepath: str) -> Optional[Dict[str, Any]]:
    """Loads a scenario from a local JSON file."""
    try:
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def export_scenario_to_json_str(scenario_data: Dict[str, Any]) -> str:
    """Serializes scenario to formatted JSON string."""
    return json.dumps(scenario_data, indent=2, ensure_ascii=False)


def import_scenario_from_json_str(json_str: str) -> Dict[str, Any]:
    """Parses JSON string into scenario dictionary."""
    return json.loads(json_str)


def export_results_to_csv(simulation_results: Dict[str, Any]) -> str:
    """Exports structured simulation decision results to CSV string."""
    rows = []
    for opt_key, opt in simulation_results.get("options", {}).items():
        rows.append({
            "Option Key": opt_key,
            "Option Name": opt.option_name,
            "Sellable Quantity (kg)": round(opt.sellable_kg, 2),
            "Spoilage Loss (%)": round(opt.spoilage_pct, 2),
            "Gross Revenue (INR)": round(opt.gross_revenue, 2),
            "Storage Cost (INR)": round(opt.storage_cost, 2),
            "Transport Cost (INR)": round(opt.transport_cost, 2),
            "Total Operating Cost (INR)": round(opt.total_operating_cost, 2),
            "Net Farmer Value (INR)": round(opt.net_farmer_value, 2),
            "Unit Net Value (INR/kg)": round(opt.unit_net_value, 2)
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
