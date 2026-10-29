"""
HarvestWise AI — Localization & Bilingual Support (English & Tamil / தமிழ்)
Provides comprehensive translations for UI elements, labels, messages, and tooltips.
"""

TRANSLATIONS = {
    "en": {
        # App Header & Meta
        "app_title": "HarvestWise AI",
        "app_subtitle": "Harvest Timing & Market Option Simulator — Phase 3",
        "app_disclaimer": "Academic Phase 3 Decision Support Prototype. Calculations are scenario-based heuristics using user-provided assumptions, not live forecasts. Always verify with local agricultural extension officers before commercial harvest.",
        "offline_badge": "🟢 Fully Offline Capable • Local Execution",
        "synthetic_badge": "ℹ️ Synthetic Scenario Assumptions",
        "manual_entry_badge": "✍️ Manual Field Data Entry",

        # Navigation
        "nav_title": "Navigation",
        "nav_overview": "🌾 Overview Dashboard",
        "nav_field_capture": "📝 Field Data Capture",
        "nav_simulator": "⚡ Harvest & Market Simulator",
        "nav_scenarios": "📊 Scenario Comparison (A, B, C)",
        "nav_sensitivity": "📈 Sensitivity Analysis",
        "nav_tests": "🧪 Automated Test Suite",
        "nav_report": "📄 Phase 3 Evaluation Report",
        "nav_settings": "⚙️ Settings & Offline Workflow",

        # Languages
        "language_select": "Language / மொழி",
        "lang_en": "English",
        "lang_ta": "தமிழ் (Tamil)",

        # Crop & Farm Inputs
        "crop_name": "Select Crop",
        "crop_tomato": "Tomato (தக்காளி)",
        "crop_banana": "Banana (வாழை)",
        "crop_mango": "Mango (மாம்பழம்)",
        "crop_onion": "Onion (வெங்காயம்)",
        "crop_potato": "Potato (உருளைக்கிழங்கு)",
        "crop_chili": "Green Chili (பச்சை மிளகாய்)",
        "crop_paddy": "Paddy / Rice (நெல்)",
        "crop_other": "Other Produce (பிற விளைபொருள்)",
        
        "quantity_kg": "Total Harvest Quantity (kg)",
        "quantity_kg_help": "Estimated weight of the crop ready or near-ready for harvest.",
        "maturity_pct": "Estimated Crop Maturity (%)",
        "maturity_pct_help": "Maturity status. Below 65% is considered immature for immediate harvest.",
        "current_price": "Nearby Market Spot Price (₹/kg)",
        "future_price": "Expected Future Price after Waiting (₹/kg)",
        "alt_price": "Alternate / Distant Market Price (₹/kg)",
        "base_spoilage_pct": "Baseline Inherent Spoilage Rate (%)",
        "base_spoilage_pct_help": "Expected natural loss under ideal conditions.",
        "wait_days": "Waiting Period (Days)",
        "wait_days_help": "Number of days delaying harvest or sale to wait for price rise.",
        "storage_cost": "Storage Cost (₹/kg/day)",
        "storage_cost_help": "Daily cost of cold storage, warehouse rental, or on-farm drying.",
        "transport_cost_nearby": "Nearby Market Transport Cost (₹ total)",
        "transport_hours_nearby": "Nearby Transport Time (hours)",
        "transport_cost_alt": "Alternate Market Transport Cost (₹ total)",
        "transport_hours_alt": "Alternate Transport Time (hours)",
        "weather_risk": "Current / Forecast Weather Risk",
        "weather_low": "Low (Clear / Dry)",
        "weather_mod": "Moderate (Humid / Overcast)",
        "weather_high": "High (Heavy Rain / Storm)",
        "storage_quality": "Storage Condition / Facility",
        "storage_good": "Good (Cold Storage / Ventilated Shed)",
        "storage_avg": "Average (Covered Farm Yard)",
        "storage_poor": "Poor (Open Air / Direct Moisture)",
        "nearby_market_name": "Nearby Market Name",
        "alt_market_name": "Alternate Market Name",

        # Options
        "opt_harvest_now": "Harvest Now",
        "opt_wait": "Wait for Better Price",
        "opt_alt_market": "Alternate Market",

        # Metrics & Results
        "recommendation": "Recommended Decision",
        "recommended_reason": "Decision Explanation",
        "crossover_conditions": "Critical Assumptions & Tipping Points",
        "net_farmer_value": "Estimated Net Farmer Value",
        "sellable_quantity": "Sellable Quantity",
        "expected_spoilage": "Effective Spoilage Loss",
        "gross_revenue": "Gross Market Revenue",
        "operating_costs": "Total Operating Costs",
        "baseline_value": "Documented Baseline (Naive)",
        "baseline_diff": "Net Advantage vs Baseline",
        "storage_expense": "Incurred Storage Cost",
        "transport_expense": "Incurred Transport Cost",

        # Explanations & Advice
        "immature_warning": "⚠️ Caution: Crop maturity is below 65%. Harvesting prematurely often leads to commercial downgrading and poor shelf life. Consult your local agricultural officer.",
        "high_spoilage_alert": "🚨 Spoilage Warning: Projected loss exceeds 25%. Prolonged storage or distant transit is high risk.",
        "equal_options_note": "⚖️ Multiple options yield near-identical net returns. The system recommends the lowest risk option.",

        # Scenarios Page
        "scenario_a_title": "Scenario A: Mature Crop with Stable Weather & Nearby Market",
        "scenario_b_title": "Scenario B: Price Rise with Rainy Weather & Waiting Storage Costs",
        "scenario_c_title": "Scenario C: Higher-Price Alternate Market with Longer Transport",
        "load_scenario": "Load Scenario into Simulator",
        "compare_all_scenarios": "Run All Scenarios & Baseline Comparison",

        # Actions & Buttons
        "calculate_btn": "⚡ Run Simulation & Analyze",
        "reset_defaults": "🔄 Reset to Defaults",
        "export_csv": "📥 Export Results (CSV)",
        "export_json": "📥 Export Scenario (JSON)",
        "import_json": "📤 Import Scenario (JSON)",
        "generate_pdf": "📄 Download Phase 3 PDF Report",
        "run_tests_btn": "▶️ Run Automated Test Suite",

        # Offline & Settings
        "offline_heading": "Offline Operation & Fallback Guidelines",
        "offline_desc": "HarvestWise AI operates entirely locally on your machine without requiring continuous internet or remote APIs.",
        "fallback_heading": "Manual Observation Fallback Protocol",
        "data_status": "Data Source Mode"
    },
    "ta": {
        # App Header & Meta
        "app_title": "ஹார்வெஸ்ட்வைஸ் AI (HarvestWise AI)",
        "app_subtitle": "அறுவடை நேரம் மற்றும் சந்தை வாய்ப்பு உருவகப்படுத்தி — கட்டம் 3",
        "app_disclaimer": "கல்வி கட்டம் 3 ஆய்வுக்கான முடிவு-ஆதரவு மாதிரி. இவை உத்தேச கணக்கீடுகள் மட்டுமே. வணிக ரீதியான அறுவடைக்கு முன் உள்ளூர் வேளாண்மை விரிவாக்க அதிகாரிகளை அணுகவும்.",
        "offline_badge": "🟢 இணையம் இன்றி முழுமையாக இயங்கக்கூடியது",
        "synthetic_badge": "ℹ️ மாதிரி/செயற்கை அனுமானங்கள்",
        "manual_entry_badge": "✍️ நேரடி களத் தரவு பதிவு",

        # Navigation
        "nav_title": "வழிசெலுத்தல் (பக்கங்கள்)",
        "nav_overview": "🌾 மேலோட்டப் பலகை (Overview)",
        "nav_field_capture": "📝 களத் தரவுப் பதிவு (Field Data)",
        "nav_simulator": "⚡ அறுவடை & சந்தை உருவகப்படுத்தி (Simulator)",
        "nav_scenarios": "📊 சூழ்நிலை ஒப்பீடு (A, B, C)",
        "nav_sensitivity": "📈 உணர்திறன் பகுப்பாய்வு (Sensitivity)",
        "nav_tests": "🧪 தானியங்கி சோதனை முடிவுகள் (Tests)",
        "nav_report": "📄 கட்டம் 3 மதிப்பீட்டு அறிக்கை (Report)",
        "nav_settings": "⚙️ அமைப்புகள் & ஆஃப்லைன் நெறிமுறை (Settings)",

        # Languages
        "language_select": "மொழி / Language",
        "lang_en": "English",
        "lang_ta": "தமிழ் (Tamil)",

        # Crop & Farm Inputs
        "crop_name": "பயிர் தேர்வு",
        "crop_tomato": "தக்காளி (Tomato)",
        "crop_banana": "வாழை (Banana)",
        "crop_mango": "மாம்பழம் (Mango)",
        "crop_onion": "வெங்காயம் (Onion)",
        "crop_potato": "உருளைக்கிழங்கு (Potato)",
        "crop_chili": "பச்சை மிளகாய் (Green Chili)",
        "crop_paddy": "நெல் (Paddy / Rice)",
        "crop_other": "பிற விளைபொருள் (Other Produce)",

        "quantity_kg": "மொத்த அறுவடை அளவு (கிலோ)",
        "quantity_kg_help": "அறுவடைக்குத் தயாராக உள்ள பயிரின் உத்தேச எடை.",
        "maturity_pct": "பயிர் முதிர்ச்சி சதவீதம் (%)",
        "maturity_pct_help": "பயிர் முதிர்ச்சி நிலை. 65%க்குக் குறைவாக இருந்தால் அறுவடை பரிந்துரைக்கப்படாது.",
        "current_price": "அருகிலுள்ள சந்தை தற்போதைய விலை (₹/கிலோ)",
        "future_price": "காத்திருப்புக்குப் பின் எதிர்பார்க்கப்படும் விலை (₹/கிலோ)",
        "alt_price": "மாற்று / தூர சந்தை விலை (₹/கிலோ)",
        "base_spoilage_pct": "இயற்கை சேதாரம் / அழுகல் விகிதம் (%)",
        "base_spoilage_pct_help": "இயற்கை சூழ்நிலையில் பயிரின் உத்தேச சேதார சதவீதம்.",
        "wait_days": "காத்திருக்கும் நாட்கள்",
        "wait_days_help": "விலை உயர்வை எதிர்நோக்கி காத்திருக்கும் நாட்களின் எண்ணிக்கை.",
        "storage_cost": "சேமிப்பு கட்டணம் (₹/கிலோ/நாள்)",
        "storage_cost_help": "குளிர்சாதன கிடங்கு அல்லது சேமிப்புக் கூடம் தினசரி செலவு.",
        "transport_cost_nearby": "அருகிலுள்ள சந்தை போக்குவரத்து செலவு (₹ மொத்தம்)",
        "transport_hours_nearby": "அருகிலுள்ள சந்தை பயண நேரம் (மணிநேரம்)",
        "transport_cost_alt": "மாற்று சந்தை போக்குவரத்து செலவு (₹ மொத்தம்)",
        "transport_hours_alt": "மாற்று சந்தை பயண நேரம் (மணிநேரம்)",
        "weather_risk": "வானிலை இடர் நிலை",
        "weather_low": "குறைவு (தெளிவான / வறண்ட வானிலை)",
        "weather_mod": "மிதமானது (ஈரப்பதம் / மேகமூட்டம்)",
        "weather_high": "அதிகம் (கனமழை / புயல் காற்று)",
        "storage_quality": "சேமிப்பு வசதி தரம்",
        "storage_good": "நன்று (குளிர்சாதன கிடங்கு / காற்றோட்டமான கொட்டகை)",
        "storage_avg": "சராசரி (கூரை வேய்ந்த களம்)",
        "storage_poor": "மோசம் (திறந்த வெளி / நேரடி ஈரப்பதம்)",
        "nearby_market_name": "அருகிலுள்ள சந்தை பெயர்",
        "alt_market_name": "மாற்றுச் சந்தை பெயர்",

        # Options
        "opt_harvest_now": "உடனடி அறுவடை",
        "opt_wait": "விலை உயர்வுக்குக் காத்திருத்தல்",
        "opt_alt_market": "மாற்றுச் சந்தைக்கு அனுப்புதல்",

        # Metrics & Results
        "recommendation": "பரிந்துரைக்கப்பட்ட முடிவு",
        "recommended_reason": "முடிவிற்கான காரண விளக்கம்",
        "crossover_conditions": "முக்கிய அனுமானங்கள் மற்றும் மாறுதல் நிலைகள்",
        "net_farmer_value": "விவசாயிக்கு நிகர வருமானம்",
        "sellable_quantity": "விற்பனை செய்யக்கூடிய அளவு",
        "expected_spoilage": "எதிர்பார்க்கப்படும் சேதாரம்",
        "gross_revenue": "மொத்த சந்தை மதிப்பு",
        "operating_costs": "மொத்த இயக்க செலவுகள்",
        "baseline_value": "ஆரம்ப அடிப்படை மதிப்பு (சேதாரம் கருத்தில் கொள்ளாதது)",
        "baseline_diff": "அடிப்படையை விட கூடுதல் நன்மை",
        "storage_expense": "சேமிப்புச் செலவு",
        "transport_expense": "போக்குவரத்துச் செலவு",

        # Explanations & Advice
        "immature_warning": "⚠️ எச்சரிக்கை: பயிர் முதிர்ச்சி 65%க்குக் குறைவாக உள்ளது. முன்கூட்டியே அறுவடை செய்வது தரக் குறைப்பிற்கும் விலைக் குறைப்பிற்கும் வழிவகுக்கும்.",
        "high_spoilage_alert": "🚨 சேதார அபாயம்: உத்தேச சேதாரம் 25%க்கும் அதிகமாக உள்ளது. நீண்ட சேமிப்பு அல்லது தூர போக்குவரத்து அபாயகரமானது.",
        "equal_options_note": "⚖️ பல வாய்ப்புகள் ஒரே அளவிலான நிகர வருவாயைத் தருகின்றன. குறைந்த அபாயகரமான முடிவு பரிந்துரைக்கப்படுகிறது.",

        # Scenarios Page
        "scenario_a_title": "சூழ்நிலை A: நல்ல முதிர்ச்சி, நிலையான வானிலை மற்றும் அருகிலுள்ள சந்தை",
        "scenario_b_title": "சூழ்நிலை B: விலை உயர்வு வாய்ப்பு, மழைக்காலம் மற்றும் சேமிப்புச் செலவுகள்",
        "scenario_c_title": "சூழ்நிலை C: அதிக விலை மாற்றுச் சந்தை மற்றும் நீண்ட தூரப் போக்குவரத்து",
        "load_scenario": "இந்த சூழ்நிலையை உருவகப்படுத்தியில் ஏற்று",
        "compare_all_scenarios": "அனைத்து சூழ்நிலைகளையும் ஒப்பிடு",

        # Actions & Buttons
        "calculate_btn": "⚡ உருவகப்படுத்தி கணிப்புகளைச் செய்",
        "reset_defaults": "🔄 இயல்புநிலைக்கு மீட்டமை",
        "export_csv": "📥 முடிவுகளை பதிவிறக்கு (CSV)",
        "export_json": "📥 சூழ்நிலையை சேமி (JSON)",
        "import_json": "📤 சூழ்நிலையை ஏற்று (JSON)",
        "generate_pdf": "📄 கட்டம் 3 PDF அறிக்கையைப் பதிவிறக்கு",
        "run_tests_btn": "▶️ சோதனைகளை இயக்கு",

        # Offline & Settings
        "offline_heading": "ஆஃப்லைன் செயல்பாடு மற்றும் மாற்று நெறிமுறை",
        "offline_desc": "ஹார்வெஸ்ட்வைஸ் AI இணைய இணைப்பு அல்லது வெளிப்புற APIகள் இன்றி முழுமையாக உங்கள் கணினியிலேயே இயங்குகிறது.",
        "fallback_heading": "நேரடி களக் கவனிப்பு மாற்று நெறிமுறை",
        "data_status": "தரவு மூல நிலை"
    }
}

def get_text(key: str, lang: str = "en") -> str:
    """Retrieve translated text string for a given key and language code."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))
