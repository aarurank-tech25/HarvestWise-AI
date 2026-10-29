"""
HarvestWise AI — Input Validation & Edge Case Guardrails
Provides thorough validation, bounds-checking, and field-readiness warnings.
"""

from typing import Dict, Any, List, Tuple


VALID_WEATHER_RISKS = ["Low", "Moderate", "High"]
VALID_STORAGE_QUALITIES = ["Good", "Average", "Poor"]
VALID_CROPS = ["Tomato", "Banana", "Mango", "Onion", "Potato", "Green Chili", "Paddy / Rice", "Other"]


def validate_simulation_inputs(inputs: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    Validates all simulation parameters.
    
    Returns:
        (is_valid, errors_list, warnings_list)
        - is_valid: True if there are zero blocking errors.
        - errors_list: Blocking validation issues that prevent calculation.
        - warnings_list: Non-blocking agricultural advisories or risk alerts.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Harvest Quantity
    qty = inputs.get("quantity_kg")
    if qty is None:
        errors.append("Quantity is required.")
    elif not isinstance(qty, (int, float)):
        errors.append("Quantity must be a valid number.")
    elif qty <= 0:
        errors.append(f"Quantity must be strictly greater than zero (entered: {qty} kg).")
    elif qty > 100_000:
        warnings.append(f"Unusually large harvest quantity ({qty:,.0f} kg). Verify bulk logistics and storage capacity.")

    # 2. Maturity Percentage
    maturity = inputs.get("maturity_pct")
    if maturity is None:
        errors.append("Maturity percentage is required.")
    elif not isinstance(maturity, (int, float)):
        errors.append("Maturity percentage must be a number.")
    elif maturity < 0 or maturity > 100:
        errors.append(f"Maturity must be between 0% and 100% (entered: {maturity}%).")
    elif maturity < 65:
        warnings.append(
            f"Immature crop warning: Maturity is {maturity:.1f}% (< 65% recommended harvest threshold). "
            "Harvesting now risks market rejection, weight penalty, and rapid post-harvest shriveling."
        )

    # 3. Prices
    for price_key, label in [
        ("current_price", "Nearby market price"),
        ("future_price", "Expected future price"),
        ("alt_price", "Alternate market price")
    ]:
        p = inputs.get(price_key)
        if p is None:
            errors.append(f"{label} is required.")
        elif not isinstance(p, (int, float)):
            errors.append(f"{label} must be a number.")
        elif p < 0:
            errors.append(f"{label} cannot be negative (entered: ₹{p}).")
        elif p == 0:
            warnings.append(f"{label} is set to ₹0.00/kg. Verify if produce is unsellable or donated.")
        elif p > 500:
            warnings.append(f"{label} is unusually high (₹{p}/kg). Verify APMC market rates.")

    # 4. Spoilage
    spoilage = inputs.get("base_spoilage_pct")
    if spoilage is None:
        errors.append("Base spoilage rate is required.")
    elif not isinstance(spoilage, (int, float)):
        errors.append("Base spoilage rate must be a number.")
    elif spoilage < 0 or spoilage > 100:
        errors.append(f"Base spoilage must be between 0% and 100% (entered: {spoilage}%).")
    elif spoilage >= 40:
        warnings.append(f"Extreme spoilage warning: Base spoilage is {spoilage:.1f}%. Major post-harvest loss expected.")

    # 5. Waiting Days
    wait = inputs.get("wait_days")
    if wait is None:
        errors.append("Waiting days is required.")
    elif not isinstance(wait, (int, float)):
        errors.append("Waiting days must be an integer.")
    elif wait < 0:
        errors.append(f"Waiting days cannot be negative (entered: {wait}).")
    elif wait > 30:
        warnings.append(f"Long waiting period ({wait} days). High perishability risk without controlled atmosphere storage.")

    # 6. Storage Costs
    sc = inputs.get("storage_cost_per_kg_day")
    if sc is None:
        errors.append("Storage cost is required.")
    elif not isinstance(sc, (int, float)):
        errors.append("Storage cost must be a number.")
    elif sc < 0:
        errors.append(f"Storage cost cannot be negative (entered: ₹{sc}).")

    # 7. Transport Costs & Hours
    for tc_key, th_key, label in [
        ("transport_cost_nearby", "transport_hours_nearby", "Nearby market"),
        ("transport_cost_alt", "transport_hours_alt", "Alternate market")
    ]:
        tc = inputs.get(tc_key)
        th = inputs.get(th_key)
        
        if tc is None:
            errors.append(f"{label} transport cost is required.")
        elif not isinstance(tc, (int, float)) or tc < 0:
            errors.append(f"{label} transport cost must be a non-negative number.")
            
        if th is None:
            errors.append(f"{label} transport time is required.")
        elif not isinstance(th, (int, float)) or th < 0:
            errors.append(f"{label} transport time must be non-negative hours.")
        elif th > 24:
            warnings.append(f"{label} transport transit is {th:.1f} hours (> 24 hrs). Produce requires refrigerated reefer transport.")

    # 8. Weather Risk & Storage Facility
    weather = inputs.get("weather_risk")
    if weather not in VALID_WEATHER_RISKS:
        errors.append(f"Weather risk must be one of {VALID_WEATHER_RISKS} (entered: '{weather}').")

    storage_q = inputs.get("storage_quality")
    if storage_q not in VALID_STORAGE_QUALITIES:
        errors.append(f"Storage quality must be one of {VALID_STORAGE_QUALITIES} (entered: '{storage_q}').")

    # 9. Cross-variable check: Wait period with zero storage cost
    if (wait or 0) > 0 and (sc or 0) == 0:
        warnings.append("Waiting days entered with ₹0.00 storage cost. Note: On-farm storage may incur implicit losses.")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings
