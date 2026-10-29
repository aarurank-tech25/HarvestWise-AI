"""
Unit Tests for the HarvestWise AI Simulation Engine.
Verifies arithmetic correctness, cost separation (no double counting),
baseline calculation, tie-breaking, immaturity guardrails, and scenario logic.
"""

import unittest
from src.simulator import (
    run_simulation,
    calculate_effective_spoilage,
    WEATHER_MULTIPLIERS,
    STORAGE_MULTIPLIERS
)
from src.scenarios import REPRODUCIBLE_SCENARIOS, run_all_scenarios


class TestSimulator(unittest.TestCase):

    def setUp(self):
        self.standard_inputs = {
            "quantity_kg": 1000.0,
            "maturity_pct": 90.0,
            "current_price": 25.0,
            "future_price": 32.0,
            "alt_price": 28.0,
            "base_spoilage_pct": 5.0,
            "wait_days": 3,
            "storage_cost_per_kg_day": 0.20,
            "transport_cost_nearby": 1000.0,
            "transport_hours_nearby": 1.0,
            "transport_cost_alt": 2500.0,
            "transport_hours_alt": 4.0,
            "weather_risk": "Moderate",
            "storage_quality": "Average"
        }

    def test_cost_isolation_and_no_double_counting(self):
        """Verify operating costs are isolated properly across the three options."""
        res = run_simulation(self.standard_inputs)
        self.assertTrue(res.is_valid)

        opt_now = res.options["harvest_now"]
        opt_wait = res.options["wait_price"]
        opt_alt = res.options["alt_market"]

        # Option 1: Harvest Now must have ZERO storage cost
        self.assertEqual(opt_now.storage_cost, 0.0)
        self.assertEqual(opt_now.transport_cost, self.standard_inputs["transport_cost_nearby"])
        self.assertEqual(opt_now.total_operating_cost, opt_now.transport_cost)
        self.assertEqual(opt_now.net_farmer_value, opt_now.gross_revenue - opt_now.total_operating_cost)

        # Option 2: Wait for Price must have storage cost = Q * Days * Rate
        expected_storage = 1000.0 * 3 * 0.20  # ₹600
        self.assertAlmostEqual(opt_wait.storage_cost, expected_storage, places=2)
        self.assertEqual(opt_wait.transport_cost, self.standard_inputs["transport_cost_nearby"])
        self.assertAlmostEqual(opt_wait.total_operating_cost, expected_storage + opt_wait.transport_cost, places=2)
        self.assertAlmostEqual(opt_wait.net_farmer_value, opt_wait.gross_revenue - opt_wait.total_operating_cost, places=2)

        # Option 3: Alternate Market must have ZERO storage cost and separate alternate transport cost
        self.assertEqual(opt_alt.storage_cost, 0.0)
        self.assertEqual(opt_alt.transport_cost, self.standard_inputs["transport_cost_alt"])
        self.assertEqual(opt_alt.total_operating_cost, opt_alt.transport_cost)
        self.assertAlmostEqual(opt_alt.net_farmer_value, opt_alt.gross_revenue - opt_alt.total_operating_cost, places=2)

    def test_baseline_calculation(self):
        """Naive baseline assumes 0% spoilage and 0 waiting costs."""
        res = run_simulation(self.standard_inputs)
        expected_baseline_gross = 1000.0 * 25.0  # ₹25,000
        expected_baseline_net = expected_baseline_gross - 1000.0  # ₹24,000
        
        self.assertAlmostEqual(res.baseline_gross_revenue, expected_baseline_gross, places=2)
        self.assertAlmostEqual(res.baseline_net_value, expected_baseline_net, places=2)
        
        # Real harvest now net must be strictly lower than naive baseline due to real spoilage
        self.assertLess(res.options["harvest_now"].net_farmer_value, res.baseline_net_value)

    def test_immature_crop_guardrail(self):
        """Crops under 65% maturity trigger immaturity hold recommendation."""
        inputs = self.standard_inputs.copy()
        inputs["maturity_pct"] = 60.0
        res = run_simulation(inputs)
        
        self.assertTrue(res.is_immature)
        self.assertEqual(res.recommended_option_key, "immature_hold")
        self.assertIn("premature", res.recommendation_reason.lower())

    def test_extreme_spoilage_capped_at_98_percent(self):
        """Ensure math never produces negative sellable produce or >98% decay."""
        inputs = self.standard_inputs.copy()
        inputs["base_spoilage_pct"] = 95.0
        inputs["weather_risk"] = "High"
        inputs["storage_quality"] = "Poor"
        inputs["wait_days"] = 25
        
        res = run_simulation(inputs)
        self.assertTrue(res.is_valid)
        self.assertLessEqual(res.options["wait_price"].spoilage_pct, 98.0)
        self.assertGreaterEqual(res.options["wait_price"].sellable_kg, 20.0)  # at least 2% of 1000kg

    def test_tie_breaking_logic(self):
        """When two options give identical net values, Harvest Now is preferred due to lower risk."""
        inputs = self.standard_inputs.copy()
        # Set prices and costs such that harvest now and wait price are virtually tied
        inputs["current_price"] = 30.0
        inputs["future_price"] = 30.0
        inputs["wait_days"] = 0
        inputs["storage_cost_per_kg_day"] = 0.0
        
        res = run_simulation(inputs)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.recommended_option_key, "harvest_now")

    def test_scenario_a_reproducibility(self):
        """Scenario A: Mature crop, stable weather, minimal price spread -> Harvest Now wins."""
        sc_a = REPRODUCIBLE_SCENARIOS["A"]
        res = run_simulation(sc_a)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.recommended_option_key, "harvest_now")
        self.assertGreater(res.options["harvest_now"].net_farmer_value, res.options["wait_price"].net_farmer_value)

    def test_scenario_c_reproducibility(self):
        """Scenario C: High price alternate market overcomes freight -> Alternate Market wins."""
        sc_c = REPRODUCIBLE_SCENARIOS["C"]
        res = run_simulation(sc_c)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.recommended_option_key, "alt_market")
        self.assertGreater(res.options["alt_market"].net_farmer_value, res.options["harvest_now"].net_farmer_value)

    def test_tipping_points_generation(self):
        """Ensure decision boundary tipping points are calculated."""
        res = run_simulation(self.standard_inputs)
        self.assertTrue(res.is_valid)
        self.assertGreater(len(res.tipping_points), 0)
        self.assertTrue(any("Future Price Tipping Point" in tp for tp in res.tipping_points))


if __name__ == "__main__":
    unittest.main()
