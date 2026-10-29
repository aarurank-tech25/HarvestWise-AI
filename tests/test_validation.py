"""
Unit Tests for Input Validation and Guardrails in HarvestWise AI.
Tests edge cases, boundary conditions, negative numbers, and agronomic warnings.
"""

import unittest
from src.validation import validate_simulation_inputs


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.valid_inputs = {
            "quantity_kg": 1000.0,
            "maturity_pct": 90.0,
            "current_price": 25.0,
            "future_price": 30.0,
            "alt_price": 32.0,
            "base_spoilage_pct": 5.0,
            "wait_days": 2,
            "storage_cost_per_kg_day": 0.25,
            "transport_cost_nearby": 1000.0,
            "transport_hours_nearby": 1.5,
            "transport_cost_alt": 2500.0,
            "transport_hours_alt": 5.0,
            "weather_risk": "Moderate",
            "storage_quality": "Average"
        }

    def test_valid_inputs_pass(self):
        is_valid, errors, warnings = validate_simulation_inputs(self.valid_inputs)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_zero_quantity_fails(self):
        inputs = self.valid_inputs.copy()
        inputs["quantity_kg"] = 0.0
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)
        self.assertTrue(any("greater than zero" in e for e in errors))

    def test_negative_quantity_fails(self):
        inputs = self.valid_inputs.copy()
        inputs["quantity_kg"] = -500.0
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)
        self.assertTrue(any("greater than zero" in e for e in errors))

    def test_negative_price_fails(self):
        for price_key in ["current_price", "future_price", "alt_price"]:
            inputs = self.valid_inputs.copy()
            inputs[price_key] = -10.0
            is_valid, errors, warnings = validate_simulation_inputs(inputs)
            self.assertFalse(is_valid)
            self.assertTrue(any("cannot be negative" in e for e in errors))

    def test_negative_costs_and_times_fail(self):
        for cost_key in ["storage_cost_per_kg_day", "transport_cost_nearby", "transport_cost_alt"]:
            inputs = self.valid_inputs.copy()
            inputs[cost_key] = -50.0
            is_valid, errors, warnings = validate_simulation_inputs(inputs)
            self.assertFalse(is_valid)

        for time_key in ["transport_hours_nearby", "transport_hours_alt", "wait_days"]:
            inputs = self.valid_inputs.copy()
            inputs[time_key] = -2
            is_valid, errors, warnings = validate_simulation_inputs(inputs)
            self.assertFalse(is_valid)

    def test_immature_crop_triggers_warning(self):
        inputs = self.valid_inputs.copy()
        inputs["maturity_pct"] = 55.0  # Below 65% threshold
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertTrue(is_valid)  # Valid for simulation, but triggers critical warning
        self.assertTrue(any("Immature crop warning" in w for w in warnings))

    def test_extreme_maturity_bounds(self):
        inputs = self.valid_inputs.copy()
        inputs["maturity_pct"] = 105.0
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)

        inputs["maturity_pct"] = -5.0
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)

    def test_extreme_spoilage_warning_and_bounds(self):
        inputs = self.valid_inputs.copy()
        inputs["base_spoilage_pct"] = 45.0
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertTrue(is_valid)
        self.assertTrue(any("Extreme spoilage" in w for w in warnings))

        inputs["base_spoilage_pct"] = 120.0
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)

    def test_invalid_weather_and_storage(self):
        inputs = self.valid_inputs.copy()
        inputs["weather_risk"] = "Tornado"
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)

        inputs = self.valid_inputs.copy()
        inputs["storage_quality"] = "Sub-zero freezer"
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertFalse(is_valid)

    def test_long_transport_warning(self):
        inputs = self.valid_inputs.copy()
        inputs["transport_hours_alt"] = 30.0  # > 24 hours
        is_valid, errors, warnings = validate_simulation_inputs(inputs)
        self.assertTrue(is_valid)
        self.assertTrue(any("transport transit is" in w for w in warnings))


if __name__ == "__main__":
    unittest.main()
