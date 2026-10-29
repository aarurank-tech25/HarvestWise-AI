"""
HarvestWise AI — Harvest Timing & Market Option Simulator (Phase 3)
Complete runnable Streamlit application featuring bilingual English & Tamil interface,
multi-page navigation, non-double-counting cost simulation, baseline auditing,
scenario comparison (A, B, C), sensitivity crossover analysis, live test runner,
and downloadable PDF evaluation report.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import unittest
from datetime import datetime

from src.translations import get_text
from src.validation import validate_simulation_inputs, VALID_CROPS
from src.simulator import run_simulation, SimulationResult
from src.scenarios import (
    REPRODUCIBLE_SCENARIOS,
    get_scenario,
    run_all_scenarios,
    build_scenario_comparison_df
)
from src.sensitivity import (
    analyze_future_price_sensitivity,
    analyze_spoilage_sensitivity,
    analyze_weather_sensitivity,
    analyze_storage_cost_sensitivity,
    analyze_transport_time_sensitivity,
    analyze_wait_days_sensitivity,
    find_critical_tipping_points
)
from src.storage import (
    get_offline_fallback,
    export_scenario_to_json_str,
    import_scenario_from_json_str,
    export_results_to_csv,
    DATA_ORIGIN_SYNTHETIC,
    DATA_ORIGIN_MANUAL
)
from src.pdf_generator import generate_evaluation_pdf

# -----------------------------------------------------------------------------
# 1. Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="HarvestWise AI — Harvest Timing & Market Simulator",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Agriculture & Premium Clean UI Theme
st.markdown("""
<style>
    /* Main Background & Fonts */
    .main { background-color: #f7faf5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid #e1eadb;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    [data-testid="stMetricValue"] {
        color: #1b4332;
        font-weight: 700;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 14px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(27, 67, 50, 0.15);
    }
    .header-card h1 { color: #ffffff !important; margin: 0 0 6px 0; font-size: 28px; }
    .header-card p { color: #d8f3dc; margin: 0; font-size: 14px; }
    
    /* Badges */
    .badge-offline {
        display: inline-block;
        background-color: #d8f3dc;
        color: #1b4332;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-synthetic {
        display: inline-block;
        background-color: #fef08a;
        color: #854d0e;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-manual {
        display: inline-block;
        background-color: #dbeafe;
        color: #1e40af;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #2d6a4f;
        color: #2d6a4f;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Session State Initialization
# -----------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state.lang = "en"

if "current_scenario_id" not in st.session_state:
    st.session_state.current_scenario_id = "A"

if "sim_inputs" not in st.session_state:
    st.session_state.sim_inputs = get_scenario("A")
    st.session_state.data_origin = DATA_ORIGIN_SYNTHETIC

if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = run_simulation(st.session_state.sim_inputs)


def t(key: str) -> str:
    """Helper to fetch translated text."""
    return get_text(key, st.session_state.lang)


# -----------------------------------------------------------------------------
# 3. Sidebar Navigation & Global Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌾 HarvestWise AI")
    st.caption("Phase 3 • Academic Prototype")
    
    # Language Toggle
    selected_lang = st.selectbox(
        "🌐 " + t("language_select"),
        options=["English", "தமிழ் (Tamil)"],
        index=0 if st.session_state.lang == "en" else 1
    )
    new_lang = "ta" if "தமிழ்" in selected_lang else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.markdown(f'<span class="badge-offline">{t("offline_badge")}</span>', unsafe_allow_html=True)
    if st.session_state.get("data_origin") == DATA_ORIGIN_MANUAL:
        st.markdown(f'<span class="badge-manual">{t("manual_entry_badge")}</span>', unsafe_allow_html=True)
    else:
        st.markdown(f'<span class="badge-synthetic">{t("synthetic_badge")}</span>', unsafe_allow_html=True)

    st.divider()

    # Page Navigation
    pages = [
        t("nav_overview"),
        t("nav_field_capture"),
        t("nav_simulator"),
        t("nav_scenarios"),
        t("nav_sensitivity"),
        t("nav_tests"),
        t("nav_report"),
        t("nav_settings")
    ]
    
    selected_page = st.radio(
        t("nav_title"),
        pages,
        index=0
    )

    st.divider()

    # Preset Quick Loader in Sidebar
    st.subheader("⚡ Quick Load Scenario")
    preset_choice = st.selectbox(
        "Choose Preset",
        ["A: Mature Crop & Stable Weather", "B: Rainy Weather & Price Rise", "C: Alternate Market Arbitrage"]
    )
    if st.button("Load Preset"):
        key = preset_choice[0]
        st.session_state.current_scenario_id = key
        st.session_state.sim_inputs = get_scenario(key)
        st.session_state.data_origin = DATA_ORIGIN_SYNTHETIC
        st.session_state.simulation_result = run_simulation(st.session_state.sim_inputs)
        st.success(f"Loaded {preset_choice}!")
        st.rerun()


# -----------------------------------------------------------------------------
# 4. Page 1: Overview Dashboard
# -----------------------------------------------------------------------------
if selected_page == t("nav_overview"):
    st.markdown(f"""
    <div class="header-card">
        <h1>🌾 {t("app_title")}</h1>
        <p>{t("app_subtitle")}</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(f"ℹ️ **Disclaimer:** {t('app_disclaimer')}")

    col_hero1, col_hero2 = st.columns([3, 2])
    with col_hero1:
        st.subheader("Decision Support Paradigm")
        st.write(
            "HarvestWise AI assists smallholder farmers and agricultural extension officers in evaluating "
            "the three fundamental commercial pathways available at crop maturity:"
        )
        st.markdown("""
        1. **Harvest Now:** Sell immediately at the nearby market spot price. Incurs zero holding costs and zero additional spoilage.
        2. **Wait for Better Price:** Delay harvest or hold in local storage expecting price recovery. Incurs daily storage rent and decay risk.
        3. **Alternate Market:** Transport produce to a distant terminal wholesale market offering price premiums. Incurs higher freight and transit vibration losses.
        """)
        st.write(
            "**Core Innovation:** Transparent, non-double-counting economic accounting with biological decay adjustments, "
            "directly compared against the conventional naive smallholder baseline."
        )

    with col_hero2:
        st.subheader("Current Active Scenario Status")
        sim = st.session_state.simulation_result
        if sim.is_valid:
            st.metric(t("recommendation"), sim.recommended_option_name)
            st.metric(t("net_farmer_value"), f"₹{sim.recommended_net_value:,.0f}")
            st.metric(t("baseline_value"), f"₹{sim.baseline_net_value:,.0f}")
        else:
            st.error("Current scenario has input validation errors.")

    st.divider()

    # Three Quick Scenario Highlights
    st.subheader("Reproducible Academic Experiments (At a Glance)")
    sc_df = build_scenario_comparison_df(run_all_scenarios())
    st.dataframe(sc_df, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# 5. Page 2: Field Data Capture
# -----------------------------------------------------------------------------
elif selected_page == t("nav_field_capture"):
    st.markdown(f"""
    <div class="header-card">
        <h1>📝 {t("nav_field_capture")}</h1>
        <p>Record field observations, crop conditions, and market price assumptions.</p>
    </div>
    """, unsafe_allow_html=True)

    inp = st.session_state.sim_inputs

    with st.form("field_capture_form"):
        st.subheader("1. Crop & Physical Harvest Estimates")
        col1, col2, col3 = st.columns(3)
        with col1:
            crop_name = st.selectbox(
                t("crop_name"),
                ["Tomato", "Banana", "Mango", "Onion", "Potato", "Green Chili", "Paddy / Rice", "Other"],
                index=["Tomato", "Banana", "Mango", "Onion", "Potato", "Green Chili", "Paddy / Rice", "Other"].index(
                    inp.get("crop_name", "Tomato") if inp.get("crop_name") in ["Tomato", "Banana", "Mango", "Onion", "Potato", "Green Chili", "Paddy / Rice", "Other"] else "Tomato"
                )
            )
            quantity_kg = st.number_input(t("quantity_kg"), min_value=1.0, max_value=100000.0, value=float(inp.get("quantity_kg", 1000.0)), step=50.0)
            maturity_pct = st.slider(t("maturity_pct"), min_value=0.0, max_value=100.0, value=float(inp.get("maturity_pct", 90.0)), step=1.0)
        
        with col2:
            base_spoilage_pct = st.slider(t("base_spoilage_pct"), min_value=0.0, max_value=60.0, value=float(inp.get("base_spoilage_pct", 5.0)), step=0.5)
            weather_risk = st.selectbox(t("weather_risk"), ["Low", "Moderate", "High"], index=["Low", "Moderate", "High"].index(inp.get("weather_risk", "Moderate")))
            storage_quality = st.selectbox(t("storage_quality"), ["Good", "Average", "Poor"], index=["Good", "Average", "Poor"].index(inp.get("storage_quality", "Average")))

        with col3:
            wait_days = st.number_input(t("wait_days"), min_value=0, max_value=30, value=int(inp.get("wait_days", 2)), step=1)
            storage_cost = st.number_input(t("storage_cost"), min_value=0.0, max_value=5.0, value=float(inp.get("storage_cost_per_kg_day", 0.25)), step=0.05)

        st.subheader("2. Market Price & Logistics Assumptions")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("**Nearby Mandi / Market**")
            market_nearby_name = st.text_input(t("nearby_market_name"), value=inp.get("market_nearby_name", "Local Village Mandi"))
            current_price = st.number_input(t("current_price"), min_value=0.0, max_value=500.0, value=float(inp.get("current_price", 25.0)), step=1.0)
            future_price = st.number_input(t("future_price"), min_value=0.0, max_value=500.0, value=float(inp.get("future_price", 30.0)), step=1.0)
            transport_cost_nearby = st.number_input(t("transport_cost_nearby"), min_value=0.0, max_value=50000.0, value=float(inp.get("transport_cost_nearby", 1000.0)), step=50.0)
            transport_hours_nearby = st.number_input(t("transport_hours_nearby"), min_value=0.0, max_value=48.0, value=float(inp.get("transport_hours_nearby", 1.0)), step=0.5)

        with col_m2:
            st.markdown("**Alternate / Distant Terminal Market**")
            market_alt_name = st.text_input(t("alt_market_name"), value=inp.get("market_alt_name", "Distant Wholesale APMC"))
            alt_price = st.number_input(t("alt_price"), min_value=0.0, max_value=500.0, value=float(inp.get("alt_price", 32.0)), step=1.0)
            transport_cost_alt = st.number_input(t("transport_cost_alt"), min_value=0.0, max_value=100000.0, value=float(inp.get("transport_cost_alt", 2800.0)), step=100.0)
            transport_hours_alt = st.number_input(t("transport_hours_alt"), min_value=0.0, max_value=72.0, value=float(inp.get("transport_hours_alt", 5.0)), step=0.5)

        submitted = st.form_submit_button(f"💾 Save & {t('calculate_btn')}")

        if submitted:
            new_inputs = {
                "crop_name": crop_name,
                "quantity_kg": quantity_kg,
                "maturity_pct": maturity_pct,
                "current_price": current_price,
                "future_price": future_price,
                "alt_price": alt_price,
                "base_spoilage_pct": base_spoilage_pct,
                "wait_days": wait_days,
                "storage_cost_per_kg_day": storage_cost,
                "transport_cost_nearby": transport_cost_nearby,
                "transport_hours_nearby": transport_hours_nearby,
                "transport_cost_alt": transport_cost_alt,
                "transport_hours_alt": transport_hours_alt,
                "weather_risk": weather_risk,
                "storage_quality": storage_quality,
                "market_nearby_name": market_nearby_name,
                "market_alt_name": market_alt_name
            }
            is_valid, errors, warnings = validate_simulation_inputs(new_inputs)
            if not is_valid:
                for err in errors:
                    st.error(f"❌ {err}")
            else:
                st.session_state.sim_inputs = new_inputs
                st.session_state.data_origin = DATA_ORIGIN_MANUAL
                st.session_state.simulation_result = run_simulation(new_inputs)
                st.success("✅ Field data successfully updated and simulation re-run!")
                if warnings:
                    for w in warnings:
                        st.warning(f"⚠️ {w}")


# -----------------------------------------------------------------------------
# 6. Page 3: Harvest & Market Simulator
# -----------------------------------------------------------------------------
elif selected_page == t("nav_simulator"):
    st.markdown(f"""
    <div class="header-card">
        <h1>⚡ {t("nav_simulator")}</h1>
        <p>Comparative valuation across Harvest Now, Wait for Better Price, and Alternate Market.</p>
    </div>
    """, unsafe_allow_html=True)

    sim = st.session_state.simulation_result

    if not sim.is_valid:
        st.error("Simulation halted due to input errors:")
        for err in sim.errors:
            st.error(f"• {err}")
    else:
        # Warnings
        if sim.warnings:
            for w in sim.warnings:
                st.warning(f"⚠️ {w}")

        # Guardrail Alert: Immature Crop
        if sim.is_immature:
            st.error(t("immature_warning"))

        # Top Metric Ribbon
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(t("recommendation"), sim.recommended_option_name)
        col2.metric(t("net_farmer_value"), f"₹{sim.recommended_net_value:,.0f}")
        col3.metric(t("baseline_value"), f"₹{sim.baseline_net_value:,.0f}")
        diff = sim.recommended_net_value - sim.baseline_net_value
        col4.metric(t("baseline_diff"), f"₹{diff:+,.0f}")

        st.success(f"**{t('recommended_reason')}:** {sim.recommendation_reason}")

        # Tipping Points Box
        if sim.tipping_points:
            with st.expander(f"🔍 {t('crossover_conditions')}", expanded=True):
                for tp in sim.tipping_points:
                    st.markdown(f"• {tp}")

        st.divider()

        # Visual Comparison Charts
        col_chart1, col_chart2 = st.columns(2)
        
        opt_now = sim.options["harvest_now"]
        opt_wait = sim.options["wait_price"]
        opt_alt = sim.options["alt_market"]

        with col_chart1:
            st.subheader("Net Farmer Value Comparison (₹)")
            chart_df = pd.DataFrame({
                "Option": [opt_now.option_name, opt_wait.option_name, opt_alt.option_name],
                "Net Farmer Value (₹)": [opt_now.net_farmer_value, opt_wait.net_farmer_value, opt_alt.net_farmer_value],
                "Color": ["#2d6a4f", "#e07a5f", "#3d5a80"]
            })
            fig_bar = px.bar(
                chart_df,
                x="Option",
                y="Net Farmer Value (₹)",
                color="Option",
                color_discrete_sequence=["#2d6a4f", "#e07a5f", "#3d5a80"],
                text="Net Farmer Value (₹)"
            )
            fig_bar.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
            fig_bar.update_layout(showlegend=False, yaxis_title="Net Value (INR)", height=380)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_chart2:
            st.subheader("Revenue vs Cost Breakdown")
            breakdown_df = pd.DataFrame({
                "Option": [opt_now.option_name, opt_wait.option_name, opt_alt.option_name],
                "Gross Revenue": [opt_now.gross_revenue, opt_wait.gross_revenue, opt_alt.gross_revenue],
                "Storage Cost": [opt_now.storage_cost, opt_wait.storage_cost, opt_alt.storage_cost],
                "Transport Cost": [opt_now.transport_cost, opt_wait.transport_cost, opt_alt.transport_cost]
            })
            fig_breakdown = go.Figure(data=[
                go.Bar(name='Gross Revenue', x=breakdown_df['Option'], y=breakdown_df['Gross Revenue'], marker_color='#52b788'),
                go.Bar(name='Storage Cost', x=breakdown_df['Option'], y=breakdown_df['Storage Cost'], marker_color='#e63946'),
                go.Bar(name='Transport Cost', x=breakdown_df['Option'], y=breakdown_df['Transport Cost'], marker_color='#f4a261')
            ])
            fig_breakdown.update_layout(barmode='group', height=380, yaxis_title="Amount (INR)")
            st.plotly_chart(fig_breakdown, use_container_width=True)

        # Tabular Itemized Breakdown
        st.subheader("Detailed Non-Double-Counting Financial Audit")
        audit_table = [
            {
                "Parameter": "Effective Spoilage (%)",
                opt_now.option_name: f"{opt_now.spoilage_pct:.1f}%",
                opt_wait.option_name: f"{opt_wait.spoilage_pct:.1f}%",
                opt_alt.option_name: f"{opt_alt.spoilage_pct:.1f}%"
            },
            {
                "Parameter": "Sellable Weight (kg)",
                opt_now.option_name: f"{opt_now.sellable_kg:,.1f} kg",
                opt_wait.option_name: f"{opt_wait.sellable_kg:,.1f} kg",
                opt_alt.option_name: f"{opt_alt.sellable_kg:,.1f} kg"
            },
            {
                "Parameter": "Gross Revenue (₹)",
                opt_now.option_name: f"₹{opt_now.gross_revenue:,.2f}",
                opt_wait.option_name: f"₹{opt_wait.gross_revenue:,.2f}",
                opt_alt.option_name: f"₹{opt_alt.gross_revenue:,.2f}"
            },
            {
                "Parameter": "Storage Cost Incurred (₹)",
                opt_now.option_name: f"₹{opt_now.storage_cost:,.2f} (Zero)",
                opt_wait.option_name: f"₹{opt_wait.storage_cost:,.2f}",
                opt_alt.option_name: f"₹{opt_alt.storage_cost:,.2f} (Zero)"
            },
            {
                "Parameter": "Transport Freight Incurred (₹)",
                opt_now.option_name: f"₹{opt_now.transport_cost:,.2f}",
                opt_wait.option_name: f"₹{opt_wait.transport_cost:,.2f}",
                opt_alt.option_name: f"₹{opt_alt.transport_cost:,.2f}"
            },
            {
                "Parameter": "Total Operating Expenses (₹)",
                opt_now.option_name: f"₹{opt_now.total_operating_cost:,.2f}",
                opt_wait.option_name: f"₹{opt_wait.total_operating_cost:,.2f}",
                opt_alt.option_name: f"₹{opt_alt.total_operating_cost:,.2f}"
            },
            {
                "Parameter": "Net Farmer Value (₹)",
                opt_now.option_name: f"₹{opt_now.net_farmer_value:,.2f}",
                opt_wait.option_name: f"₹{opt_wait.net_farmer_value:,.2f}",
                opt_alt.option_name: f"₹{opt_alt.net_farmer_value:,.2f}"
            },
            {
                "Parameter": "Net Realization (₹/kg original)",
                opt_now.option_name: f"₹{opt_now.unit_net_value:.2f}/kg",
                opt_wait.option_name: f"₹{opt_wait.unit_net_value:.2f}/kg",
                opt_alt.option_name: f"₹{opt_alt.unit_net_value:.2f}/kg"
            }
        ]
        st.dataframe(pd.DataFrame(audit_table), use_container_width=True, hide_index=True)

        # Download Buttons
        col_d1, col_d2 = st.columns(2)
        csv_data = export_results_to_csv({"options": sim.options})
        col_d1.download_button(
            t("export_csv"),
            csv_data,
            file_name=f"harvestwise_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        json_data = export_scenario_to_json_str(st.session_state.sim_inputs)
        col_d2.download_button(
            t("export_json"),
            json_data,
            file_name=f"harvestwise_scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


# -----------------------------------------------------------------------------
# 7. Page 4: Scenario Comparison (A, B, C)
# -----------------------------------------------------------------------------
elif selected_page == t("nav_scenarios"):
    st.markdown(f"""
    <div class="header-card">
        <h1>📊 {t("nav_scenarios")}</h1>
        <p>Three core reproducible scenarios benchmarked against naive mental baseline accounting.</p>
    </div>
    """, unsafe_allow_html=True)

    all_results = run_all_scenarios()
    comp_df = build_scenario_comparison_df(all_results)

    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Download Scenarios Benchmark Table (CSV)",
        comp_df.to_csv(index=False),
        file_name="harvestwise_reproducible_scenarios_comparison.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("Scenario Deep Dives")
    tab_a, tab_b, tab_c = st.tabs([
        "Scenario A: Stable Weather",
        "Scenario B: Rainy Weather & Price Rise",
        "Scenario C: Alternate Market Arbitrage"
    ])

    for tab, sc_id in zip([tab_a, tab_b, tab_c], ["A", "B", "C"]):
        sc_data = REPRODUCIBLE_SCENARIOS[sc_id]
        res = all_results[sc_id]
        with tab:
            st.markdown(f"**{sc_data['name']}**")
            st.caption(f"Hypothesis: {sc_data['hypothesis']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Recommended Option", res.recommended_option_name)
            col2.metric("Max Net Value", f"₹{res.recommended_net_value:,.0f}")
            col3.metric("Naive Baseline", f"₹{res.baseline_net_value:,.0f}")
            overest = res.baseline_net_value - res.options["harvest_now"].net_farmer_value
            col4.metric("Baseline Spoilage Neglect", f"₹{overest:,.0f}")
            st.info(f"**Explanation:** {res.recommendation_reason}")


# -----------------------------------------------------------------------------
# 8. Page 5: Sensitivity Analysis
# -----------------------------------------------------------------------------
elif selected_page == t("nav_sensitivity"):
    st.markdown(f"""
    <div class="header-card">
        <h1>📈 {t("nav_sensitivity")}</h1>
        <p>Parametric sweeps showing exact crossover thresholds where the optimal decision changes.</p>
    </div>
    """, unsafe_allow_html=True)

    curr_inputs = st.session_state.sim_inputs

    sens_variable = st.selectbox(
        "Select Parameter to Sweep",
        [
            "Expected Future Price (₹/kg)",
            "Base Spoilage Rate (%)",
            "Weather Risk (Low, Moderate, High)",
            "Storage Cost (₹/kg/day)",
            "Alternate Market Transport Time (Hours)",
            "Waiting Duration (Days)"
        ]
    )

    if sens_variable == "Expected Future Price (₹/kg)":
        sweep_df = analyze_future_price_sensitivity(curr_inputs)
        x_col = "Future Price (₹/kg)"
    elif sens_variable == "Base Spoilage Rate (%)":
        sweep_df = analyze_spoilage_sensitivity(curr_inputs)
        x_col = "Base Spoilage (%)"
    elif sens_variable == "Weather Risk (Low, Moderate, High)":
        sweep_df = analyze_weather_sensitivity(curr_inputs)
        x_col = "Weather Condition"
    elif sens_variable == "Storage Cost (₹/kg/day)":
        sweep_df = analyze_storage_cost_sensitivity(curr_inputs)
        x_col = "Storage Cost (₹/kg/day)"
    elif sens_variable == "Alternate Market Transport Time (Hours)":
        sweep_df = analyze_transport_time_sensitivity(curr_inputs)
        x_col = "Alt Transport Hours"
    else:
        sweep_df = analyze_wait_days_sensitivity(curr_inputs)
        x_col = "Waiting Duration (Days)"

    # Plot Sensitivity Trajectory
    if x_col != "Weather Condition":
        fig_sens = px.line(
            sweep_df,
            x=x_col,
            y=["Harvest Now (₹)", "Wait (₹)", "Alternate Market (₹)"],
            markers=True,
            title=f"Decision Boundary Trajectory vs {sens_variable}"
        )
        fig_sens.update_layout(yaxis_title="Net Farmer Value (₹)", height=420)
        st.plotly_chart(fig_sens, use_container_width=True)

    st.subheader("Parametric Sensitivity Audit Table")
    st.dataframe(sweep_df, use_container_width=True, hide_index=True)

    # Highlight any decision flips
    flips = sweep_df[sweep_df["Decision Flip"] != ""]
    if not flips.empty:
        st.warning(f"⚡ **Identified Decision Boundary Crossovers:**")
        for _, r in flips.iterrows():
            st.markdown(f"• At **{x_col} = {r[x_col]}**: {r['Decision Flip']}")
    else:
        st.info("ℹ️ No decision crossover detected across this parametric range.")


# -----------------------------------------------------------------------------
# 9. Page 6: Automated Test Results
# -----------------------------------------------------------------------------
elif selected_page == t("nav_tests"):
    st.markdown(f"""
    <div class="header-card">
        <h1>🧪 {t("nav_tests")}</h1>
        <p>Live execution of unit and edge-case test suites directly in Streamlit.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write(
        "Run the internal automated regression test suite covering validation guardrails, "
        "bounds enforcement, tie-breaking, baseline accuracy, and cost separation."
    )

    if st.button(t("run_tests_btn")):
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Load from test modules
        from tests import test_simulator, test_validation
        suite.addTests(loader.loadTestsFromModule(test_validation))
        suite.addTests(loader.loadTestsFromModule(test_simulator))
        
        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        test_result = runner.run(suite)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Tests Executed", test_result.testsRun)
        col2.metric("Failures", len(test_result.failures))
        col3.metric("Errors", len(test_result.errors))

        if test_result.wasSuccessful():
            st.success(f"✅ All {test_result.testsRun} automated test cases passed with zero errors!")
        else:
            st.error("❌ Some test cases encountered issues.")

        st.subheader("Detailed Execution Log")
        st.code(stream.getvalue(), language="text")


# -----------------------------------------------------------------------------
# 10. Page 7: Evaluation Report & PDF Export
# -----------------------------------------------------------------------------
elif selected_page == t("nav_report"):
    st.markdown(f"""
    <div class="header-card">
        <h1>📄 {t("nav_report")}</h1>
        <p>Complete academic Phase 3 evaluation document, deployment checklist, and downloadable PDF.</p>
    </div>
    """, unsafe_allow_html=True)

    all_results = run_all_scenarios()
    comp_df = build_scenario_comparison_df(all_results)

    # PDF Download Button
    pdf_bytes = generate_evaluation_pdf(comp_df)
    st.download_button(
        label=t("generate_pdf"),
        data=pdf_bytes,
        file_name=f"HarvestWise_AI_Phase3_Evaluation_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

    st.divider()

    # Render Markdown Report
    try:
        with open("outputs/evaluation_report.md", "r", encoding="utf-8") as f:
            report_md = f.read()
        st.markdown(report_md)
    except Exception as e:
        st.error(f"Could not load evaluation report: {e}")


# -----------------------------------------------------------------------------
# 11. Page 8: Settings and Offline Workflow
# -----------------------------------------------------------------------------
elif selected_page == t("nav_settings"):
    st.markdown(f"""
    <div class="header-card">
        <h1>⚙️ {t("nav_settings")}</h1>
        <p>{t("offline_heading")}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("1. Offline Operation Verification")
    st.markdown("""
    - **No Cloud Dependency:** HarvestWise AI performs all calculations locally in memory.
    - **No Secret API Keys:** No remote weather forecast or mandi API calls are required.
    - **Local Persistence:** All scenario saving/loading uses standard local JSON files.
    """)

    st.divider()

    st.subheader(f"2. {t('fallback_heading')}")
    st.write(
        "When real-time market prices or meteorological radars are inaccessible, "
        "use regional horticultural benchmarks as an offline baseline:"
    )

    crop_sel = st.selectbox("Select Crop for Benchmark Guidance", VALID_CROPS)
    fallback_info = get_offline_fallback(crop_sel)
    col1, col2, col3 = st.columns(3)
    col1.metric("Fallback Spot Price", f"₹{fallback_info['fallback_spot_price']:.2f}/kg")
    col2.metric("Fallback Spoilage Rate", f"{fallback_info['fallback_spoilage_pct']:.1f}%")
    col3.metric("Conservative Weather", fallback_info["fallback_weather"])
    st.info(f"**Agronomic Advisory:** {fallback_info['advisory']}")

    st.divider()

    st.subheader("3. Scenario Import / Export (JSON)")
    col_exp, col_imp = st.columns(2)
    with col_exp:
        st.write("Export Current Active Scenario:")
        json_str = export_scenario_to_json_str(st.session_state.sim_inputs)
        st.download_button(
            "📥 Download Active Scenario (JSON)",
            json_str,
            file_name="harvestwise_active_scenario.json",
            mime="application/json"
        )

    with col_imp:
        st.write("Import Scenario from JSON:")
        uploaded_file = st.file_uploader("Upload Scenario JSON", type=["json"])
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode("utf-8")
                imported_dict = import_scenario_from_json_str(content)
                is_valid, errs, warns = validate_simulation_inputs(imported_dict)
                if is_valid:
                    st.session_state.sim_inputs = imported_dict
                    st.session_state.data_origin = DATA_ORIGIN_MANUAL
                    st.session_state.simulation_result = run_simulation(imported_dict)
                    st.success("Successfully imported and activated scenario!")
                    st.rerun()
                else:
                    for err in errs:
                        st.error(f"Import Error: {err}")
            except Exception as ex:
                st.error(f"Failed to parse JSON file: {ex}")

st.divider()
st.caption("🌾 HarvestWise AI • Academic Phase 3 Final Submission • Pure Local Offline Execution • Synthetic Scenario Demonstrations")
