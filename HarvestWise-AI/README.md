# HarvestWise AI — Harvest Timing & Market Option Simulator
**Phase 3 Final Submission**  
*Academic Decision-Support Prototype for Smallholder Horticulture Producers*

---

## 🌾 Project Overview

**HarvestWise AI** is an explainable, deterministic agricultural technology decision-support simulator. It evaluates the economic and biological trade-offs faced by smallholder farmers when deciding whether to:
1. **Harvest Now:** Sell immediately at the local village mandi.
2. **Wait for Better Price:** Delay harvest or store produce on-farm to wait for anticipated market price increases.
3. **Alternate Market:** Transport produce to a distant terminal wholesale market offering price premiums.

### Key Innovations in Phase 3
- **Strict Non-Double-Counting Cost Isolation:** Storage costs are strictly incurred during waiting periods, while transport costs correspond to the selected destination market.
- **Biological Decay & Spoilage Adjustment:** Dynamically computes post-harvest losses based on crop maturity, ambient weather risk (rain/humidity), storage facility quality, and transit duration.
- **Naive Smallholder Baseline Auditing:** Benchmarks every recommendation against standard mental accounting (`Quantity × Spot Price - Transport`), exposing how unmodeled spoilage and holding fees create phantom profits.
- **Automated Crossover Sensitivity Analysis:** Parametrically sweeps price spreads, storage fees, transit hours, and decay rates to highlight exact tipping points where decisions flip.
- **Bilingual Interface:** Instant real-time toggle between **English** and **Tamil (தமிழ்)**.
- **100% Offline Capability:** Pure edge computation without cloud dependencies or live external API risks.
- **Downloadable PDF Report:** In-app generation of academic evaluation documentation using ReportLab.

---

## 📂 Project Structure

```text
HarvestWise-AI-Phase3/
│
├── app.py                                   # Complete multi-page Streamlit dashboard
├── requirements.txt                         # Python dependencies (Streamlit, Pandas, Plotly, ReportLab)
├── README.md                                # Comprehensive setup and review documentation
├── .gitignore                               # Git ignore configuration
│
├── src/                                     # Core Application Modules
│   ├── __init__.py
│   ├── simulator.py                         # Core simulation logic, cost accounting & explanations
│   ├── validation.py                        # Input validation, guardrails & edge-case warnings
│   ├── scenarios.py                         # Reproducible Scenarios (A, B, C) & baseline comparisons
│   ├── sensitivity.py                       # Parametric sensitivity engine & crossover detection
│   ├── translations.py                      # Bilingual localization dictionary (English & Tamil)
│   ├── storage.py                           # Local JSON/CSV persistence & offline fallback rules
│   └── pdf_generator.py                     # ReportLab PDF evaluation report builder
│
├── tests/                                   # Automated Regression Test Suite
│   ├── __init__.py
│   ├── test_simulator.py                    # Unit tests for arithmetic, baseline & cost isolation
│   └── test_validation.py                   # Unit tests for edge cases, bounds & immaturity alerts
│
├── data/                                    # Scenario Data & Provenance
│   └── sample_scenarios.json                # Synthetic academic scenario database with provenance tags
│
└── outputs/                                 # Academic Deliverables
    ├── evaluation_report.md                 # Full Phase 3 Evaluation Report
    └── stakeholder_validation_questionnaire.md # Stakeholder evaluation instrument (Pending field trials)
```

---

## 🚀 Quickstart & Launch Instructions (Windows)

Open PowerShell or Command Prompt in the workspace root directory:

```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
venv\Scripts\activate

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Launch the application
python -m streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 🧪 Automated Testing

To run the complete automated unit and regression test suite:

```powershell
python -m unittest discover -s tests -v
```

### Test Coverage Highlights:
- **`tests/test_validation.py`**: Zero quantity, negative prices, negative storage/transport costs, negative wait days, extreme maturity bounds, crop immaturity warnings (< 65%), extreme spoilage bounds, invalid weather categories, and long transit alerts (> 24 hrs).
- **`tests/test_simulator.py`**: Zero double-counting of costs, baseline calculation accuracy, immaturity hold recommendation, spoilage bounded $\le 98\%$, deterministic tie-breaking logic, reproducibility of Scenarios A, B, and C, and mathematical tipping-point derivation.

---

## 📊 The Three Core Scenarios

| Attribute | Scenario A | Scenario B | Scenario C |
| :--- | :--- | :--- | :--- |
| **Description** | Mature Crop & Stable Weather | Price Rise with Rain & Storage | Alternate Market Arbitrage |
| **Crop & Quantity** | Tomato (1,000 kg) | Tomato (1,000 kg) | Tomato (1,000 kg) |
| **Crop Maturity** | 92% | 88% | 95% |
| **Nearby Spot Price** | ₹30.00/kg | ₹24.00/kg | ₹25.00/kg |
| **Future / Alt Price**| ₹31.00/kg (1-day wait) | ₹35.00/kg (4-day wait) | ₹36.00/kg (Alternate APMC) |
| **Weather Risk** | Low (Clear/Dry) | High (Heavy Rain) | Moderate (Overcast) |
| **Storage Facility** | Good | Average | Good |
| **Transport Cost** | Nearby: ₹1,200 (1 hr) | Nearby: ₹1,400 (2 hrs) | Alt: ₹3,800 (7 hrs) |
| **Naive Baseline** | ₹28,800 | ₹22,600 | ₹23,800 |
| **Recommended Choice**| **Harvest Now** | **Wait for Better Price** | **Alternate Market** |
| **Core Insight** | Delaying for +₹1/kg adds decay and storage fees that exceed price gains. | High +₹11/kg price rise overcomes rain-induced decay and ₹1,400 storage fees. | +₹11/kg wholesale premium absorbs ₹3,800 freight and transit vibration losses. |

---

## 🛡️ Responsible AI & Ethical Design

1. **Non-Prescriptive Decision Support:** The system does not automate sales or harvest cuts. It provides scenario simulations to support farmer agency.
2. **Immaturity Protection:** Any crop below 65% maturity triggers an explicit warning holding back harvest recommendations.
3. **Data Minimization:** No personal farmer data (names, GPS coordinates, phone numbers) is recorded or transmitted.
4. **Honest Data Provenance:** All scenario data in this prototype is explicitly labeled as `SYNTHETIC_ACADEMIC_DEMO`. No real farmer results or financial savings are fabricated.

---

## 🌐 Multilingual Accessibility & Offline Protocol

- **Languages:** Real-time toggle between English and Tamil (தமிழ்).
- **Offline First:** All simulations run locally in RAM. No internet access or live APIs required.
- **Offline Fallback:** When market prices or weather data are unknown, built-in regional APMC benchmarks provide agronomic baseline guidance for 7 major horticultural crops.

---

## 📝 Review Demonstration Script (Academic Walkthrough)

1. **Launch:** Run `python -m streamlit run app.py` and open the dashboard.
2. **Language:** Toggle language in the sidebar between English and Tamil to showcase instant localization.
3. **Scenario A Review:** Under **Scenario Comparison**, inspect Scenario A to demonstrate why Harvest Now is optimal when price spread (+₹1/kg) cannot justify holding decay.
4. **Scenario B Review:** Inspect Scenario B to observe how a +₹11/kg price spike justifies 4 days of storage even under high rain decay.
5. **Scenario C Review:** Inspect Scenario C to demonstrate spatial arbitrage overcoming high freight costs.
6. **Sensitivity Matrix:** Go to **Sensitivity Analysis** and sweep `Future Price (₹/kg)` to observe the exact threshold (₹28.25/kg) where the decision flips from Harvest Now to Waiting.
7. **Live Test Suite:** Navigate to **Automated Test Results** and click `Run Automated Test Suite` to demonstrate live test execution passing 100% of cases.
8. **Evaluation PDF:** Open **Evaluation Report** and click `Download Phase 3 PDF Report` to inspect the generated academic summary.
