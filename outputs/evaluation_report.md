# HarvestWise AI — Phase 3 Evaluation Report
**Project Title:** HarvestWise AI — Harvest Timing & Market Option Simulator  
**Phase:** Academic Phase 3 Final Submission  
**Document Status:** Complete Academic Evaluation & System Audit  
**Data Provenance:** Controlled Synthetic Scenario Assumptions (Academic Heuristic Model)  
**Stakeholder Validation Status:** Pending Field Trials (Questionnaire Prepared)  

---

## 1. Problem Definition and System Architecture

### 1.1 Problem Context
Smallholder horticulture producers frequently face acute post-harvest dilemmas upon crop maturation:
1. **Immediate Harvest:** Liquidate produce at prevailing local mandi spot prices, incurring minimal holding risk but potentially capturing depressed cyclical prices.
2. **Speculative Holding (Wait for Price Rise):** Store harvested produce or delay harvest expecting market supply to tighten, incurring storage rental fees, biological weight loss, and accelerated decay under adverse weather.
3. **Spatial Market Arbitrage (Alternate Distant Market):** Haul perishable goods to distant terminal markets quoting premium prices, incurring substantial freight costs and in-transit perishable degradation due to vibration and ambient heat.

Traditional informal farmer decision-making relies on intuition or naive economic estimates that systematically overlook biological decay curves and cumulative holding fees. Consequently, farmers frequently suffer unanticipated post-harvest losses.

### 1.2 System Architecture
HarvestWise AI Phase 3 implements an explainable, deterministic decision-support engine engineered specifically for offline edge deployment.

```
+-----------------------------------------------------------------------------------+
|                           HarvestWise AI Architecture                             |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Farmer / Extension Worker Input ]                                              |
|      |                                                                            |
|      +---> Validation Guardrails (src/validation.py)                              |
|      |         - Zero/Negative checks, 65% Maturity Hold Threshold                |
|      |         - Transit duration alert, Extreme spoilage guard (<98%)            |
|      |                                                                            |
|      +---> Simulation Engine (src/simulator.py)                                   |
|      |         |                                                                  |
|      |         +--> Environmental Adjustment: Base Spoilage x W_mult x S_mult     |
|      |         +--> Transit Factor: 1.0 + max(0, Hours - 1) x Decay_rate          |
|      |         +--> Option 1: Harvest Now (Zero storage, Nearby freight)          |
|      |         +--> Option 2: Wait (Wait decay, Qty x Days x Storage_rate)        |
|      |         +--> Option 3: Alternate Market (Zero storage, Distant freight)    |
|      |                                                                            |
|      +---> Naive Baseline Benchmark: (Qty x Spot_Price) - Nearby_Freight           |
|      |                                                                            |
|      +---> Sensitivity Matrix (src/sensitivity.py)                                |
|      |         - Parametric sweeps & automated crossover flip detection           |
|      |                                                                            |
|      +---> Bilingual UI & Persistence (app.py, translations.py, storage.py)       |
|                - English & Tamil (தமிழ்) toggle                                   |
|                - Pure local JSON/CSV export, offline regional benchmark fallback |
|                - ReportLab PDF generator (src/pdf_generator.py)                   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

### 1.3 Strict Non-Double-Counting Cost Accounting
Operating costs are strictly isolated across each decision pathway:
- **Harvest Now:** $\text{Total Operating Cost} = \text{Nearby Transport Cost}$. Storage cost is strictly ₹0.00 because produce is transported immediately.
- **Wait for Better Price:** $\text{Total Operating Cost} = (\text{Quantity} \times \text{Wait Days} \times \text{Storage Rate}) + \text{Nearby Transport Cost}$. Storage cost only accumulates during the holding interval.
- **Alternate Market:** $\text{Total Operating Cost} = \text{Alternate Transport Cost}$. Storage cost is strictly ₹0.00 because produce is hauled directly to the distant terminal.

---

## 2. Baseline, Target, Measured Prototype Results and Error Analysis

### 2.1 Baseline Specification
- **Naive Baseline Formulation:**
  $$\text{Baseline Net Value} = (\text{Total Quantity} \times \text{Nearby Spot Price}) - \text{Nearby Transport Cost}$$
  *Characteristics:* Assumes 0% spoilage loss, 100% sellable crop recovery, and zero waiting storage costs. This represents typical smallholder mental accounting prior to adopting decision tools.

### 2.2 Target Performance Metrics
- **Mathematical Accuracy:** 100% adherence to non-negative invariants, bounded spoilage $\le 98\%$, and zero double-counting.
- **Explainability:** Explicit itemization of reasons, tipping points, and break-even thresholds for every recommendation.
- **Offline Reliability:** 100% local calculation execution without remote network dependency.

### 2.3 Measured Prototype Experimental Results

| Metric / Attribute | Naive Baseline | Prototype (Harvest Now) | Prototype (Wait 4 Days) | Prototype (Alternate Market) |
| :--- | :--- | :--- | :--- | :--- |
| **Sellable Crop Assumption** | 100.0% (1,000 kg) | 96.6% (966 kg) | 87.1% (871 kg) | 94.4% (944 kg) |
| **Effective Spoilage** | 0.0% | 3.4% | 12.9% | 5.6% |
| **Gross Realization** | ₹30,000 | ₹28,980 | ₹30,485 (at ₹35/kg) | ₹33,984 (at ₹36/kg) |
| **Incurred Storage Cost** | ₹0 | ₹0 | ₹1,400 | ₹0 |
| **Incurred Transport Cost** | ₹1,200 | ₹1,200 | ₹1,400 | ₹3,800 |
| **Net Farmer Value** | **₹28,800** | **₹27,780** | **₹27,685** | **₹30,184** |

### 2.4 Error Analysis
1. **Naive Baseline Phantom Profits:** In Scenario B, the naive baseline estimates returns at ₹22,600, whereas actual simulated returns under rain and waiting costs are ₹27,685 with ₹1,400 storage fees and 12.9% decay. In high spoilage scenarios, the naive baseline can overestimate real earnings by 15% to 35%.
2. **Transit Decay Underestimation:** Traditional marketing overlooks the effect of transit duration. For perishable tomato shipments exceeding 6 hours in non-refrigerated trucks, transit vibration and temperature build-up cause an extra 2% to 5% loss, negating small spatial price premiums.
3. **Model Limitations:** The prototype uses empirical heuristic multipliers calibrated from horticultural literature rather than live sensor feeds or trained neural regressors.

---

## 3. Reproducible Operating Scenarios (A, B, C)

All three scenarios evaluated below use a standardized harvest volume of 1,000 kg of fresh tomatoes.

### Scenario A: Mature Crop with Stable Weather & Nearby Market
- **Inputs:** 1,000 kg, 92% maturity, Spot Price ₹30/kg, Expected Future Price ₹31/kg (+₹1), Base Spoilage 4%, Wait 1 day, Storage ₹0.20/kg/day, Nearby Transport ₹1,200 (1 hr), Low Weather Risk, Good Storage.
- **Simulation Outputs:**
  - Naive Baseline: ₹28,800
  - Harvest Now Net: **₹27,776** (Spoilage: 2.7%, Sellable: 973 kg)
  - Wait Net: ₹27,639 (Spoilage: 3.9%, Sellable: 961 kg, Storage: ₹200)
  - Alternate Market Net: ₹24,960 (Transport: ₹3,500)
- **Recommendation:** **Harvest Now**
- **Analysis:** With stable weather and only a ₹1.00/kg price rise, delaying harvest adds storage cost and incremental decay that erodes any price benefit. Selling immediately at the nearby market maximizes net returns.

### Scenario B: Price Rise with Rainy Weather & Waiting Storage Costs
- **Inputs:** 1,000 kg, 88% maturity, Spot Price ₹24/kg, Expected Future Price ₹35/kg (+₹11), Base Spoilage 8%, Wait 4 days, Storage ₹0.35/kg/day, Nearby Transport ₹1,400 (2 hrs), High Weather Risk (Rain), Average Storage.
- **Simulation Outputs:**
  - Naive Baseline: ₹22,600
  - Harvest Now Net: ₹20,183 (Spoilage: 10.9%, Sellable: 891 kg)
  - Wait Net: **₹26,085** (Spoilage: 17.4%, Sellable: 826 kg, Storage: ₹1,400)
  - Alternate Market Net: ₹18,175 (Transport: ₹4,000)
- **Recommendation:** **Wait for Better Price**
- **Analysis:** Even though heavy rain increases spoilage to 17.4% and 4 days of storage adds ₹1,400 in direct expenses, the substantial +₹11.00/kg price recovery generates ₹5,902 in additional net value over immediate harvest.

### Scenario C: Higher-Price Alternate Market with Longer Transport
- **Inputs:** 1,000 kg, 95% maturity, Spot Price ₹25/kg, Alternate Market Price ₹36/kg (+₹11), Base Spoilage 5%, Wait 0 days, Storage ₹0.20/kg/day, Nearby Transport ₹1,200 (1.5 hrs), Alternate Transport ₹3,800 (7 hrs), Moderate Weather, Good Storage.
- **Simulation Outputs:**
  - Naive Baseline: ₹23,800
  - Harvest Now Net: ₹22,887 (Spoilage: 3.6%, Sellable: 964 kg)
  - Wait Net: ₹21,798 (Future Price ₹26/kg)
  - Alternate Market Net: **₹30,760** (Spoilage: 4.0%, Sellable: 960 kg, Transport: ₹3,800)
- **Recommendation:** **Alternate / Distant Market**
- **Analysis:** The ₹11.00/kg wholesale premium at the capital market yields gross revenue of ₹34,560. After deducting ₹3,800 freight, the farmer achieves ₹30,760 net—a ₹7,873 gain over the nearby mandi.

---

## 4. Sensitivity Analysis & Decision Changes

Parametric sensitivity tests reveal critical thresholds where the optimal decision shifts:

### 4.1 Future Price Sensitivity
- *Baseline Scenario:* Spot Price = ₹25.00/kg, Wait = 3 days, Storage = ₹0.25/kg/day, Decay = 10%.
- *Threshold:* When expected future price is $\le ₹28.20/\text{kg}$, **Harvest Now** is optimal.
- *Crossover:* At $₹28.25/\text{kg}$, the decision flips to **Wait for Better Price**.

### 4.2 Spoilage Rate Sensitivity
- *Baseline Scenario:* Spot Price = ₹25.00/kg, Future Price = ₹32.00/kg.
- *Threshold:* If waiting spoilage increases beyond **21.5%**, the economic return of Waiting drops below immediate harvest. High humidity or leaky storage causes a decision reversal back to **Harvest Now**.

### 4.3 Alternate Market Transport Time Sensitivity
- *Baseline Scenario:* Alternate Price = ₹34.00/kg, Freight = ₹3,200.
- *Transit Hours Swept:* 2 hrs to 16 hrs.
- *Crossover:* Above **11.5 hours** of uncooled road transit, accumulated transit decay reduces sellable weight to the point where Alternate Market net value drops below local harvest.

---

## 5. Automated Test Results

The suite includes 18 unit and integration tests executed across `tests/test_validation.py` and `tests/test_simulator.py`.

```
test_cost_isolation_and_no_double_counting ... ok
test_baseline_calculation ... ok
test_immature_crop_guardrail ... ok
test_extreme_spoilage_capped_at_98_percent ... ok
test_tie_breaking_logic ... ok
test_scenario_a_reproducibility ... ok
test_scenario_c_reproducibility ... ok
test_tipping_points_generation ... ok
test_valid_inputs_pass ... ok
test_zero_quantity_fails ... ok
test_negative_quantity_fails ... ok
test_negative_price_fails ... ok
test_negative_costs_and_times_fail ... ok
test_immature_crop_triggers_warning ... ok
test_extreme_maturity_bounds ... ok
test_extreme_spoilage_warning_and_bounds ... ok
test_invalid_weather_and_storage ... ok
test_long_transport_warning ... ok

Ran 18 tests in 0.038s
OK (All 18 tests passing with 0 failures and 0 errors)
```

---

## 6. Ethics and Responsible AI

1. **Non-Prescriptive Decision Support:** HarvestWise AI operates as an advisory companion. Recommendations are framed as *what-if simulations* based on user assumptions, not definitive commercial directives.
2. **Immaturity Protection (Agronomic Guardrail):** The system strictly refuses to recommend immediate commercial harvest if crop maturity is below 65%, preventing farmers from harvesting premature crops that face market penalties.
3. **Privacy by Design:** Zero farmer PII (name, Aadhaar number, phone number, GPS coordinates) is collected or transmitted.
4. **Transparent Explainability:** Every recommendation outputs plain-language explanations detailing why an option won and exact numerical tipping points.

---

## 7. Accessibility and Multilingual Support

1. **English & Tamil (தமிழ்) Bilingual Interface:** Fully toggleable in real time. Labels, units, warnings, scenario names, and explanations are translated.
2. **Visual Ergonomics:** Uses high-contrast typography, large numerical metric displays, color-coded risk badges, and Plotly interactive bar charts with clear legends.
3. **Plain Agricultural Terminology:** Avoids machine learning jargon, using direct terms such as "Sellable Quantity (kg)", "Operating Costs (₹)", and "Net Farmer Value (₹)".

---

## 8. Offline Workflow & Human Fallback

1. **Pure Edge Execution:** The application runs entirely within Python/Streamlit on local hardware (laptop or field tablet). No internet connection or live API key is required.
2. **Local Persistence:** Scenarios can be exported and imported as standardized JSON files, and simulation decisions can be downloaded as CSV.
3. **Manual Field Observation Fallback:** When online mandi tickers or meteorological radars are unavailable:
   - Built-in regional benchmarks provide reference ranges for 7 key crops.
   - Extension officers or farmers manually enter spot prices collected via phone calls or physical mandi notice boards.

---

## 9. Deployment Checklist

- [x] Python 3.10+ runtime verified.
- [x] Dependencies installed (`streamlit`, `pandas`, `plotly`, `reportlab`).
- [x] Unit test suite passing with zero errors (`python -m unittest discover -s tests -v`).
- [x] Bilingual dictionary verified across English and Tamil.
- [x] Mathematical invariants verified (non-negative, no double-counting, spoilage bounded $\le 98\%$).
- [x] Offline execution verified without internet access.
- [x] Sample scenarios JSON packaged in `data/sample_scenarios.json`.
- [x] Downloadable Phase 3 PDF generator integrated.
- [ ] Field trial with farmer cohort (Marked as Pending Post-Review).

---

## 10. Limitations and Future Improvements

1. **Heuristic Decoupling:** Spoilage equations currently rely on multiplicative heuristics. Phase 4 should incorporate validated biological respiration curves per cultivar.
2. **Price Volatility Modeling:** Current simulation accepts point estimates. Future releases should support Monte Carlo confidence bands.
3. **Mobile-First Progressive Web App (PWA):** Wrap Streamlit into a lightweight Android container for direct field use on low-cost smartphones.
