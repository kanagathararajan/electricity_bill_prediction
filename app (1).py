
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# Page Config
st.set_page_config(
    page_title="VoltWise | Smart Electricity Advisor",
    page_icon="⚡",
    layout="centered" if "step" in st.session_state and st.session_state.step == "login" else "wide"
)

# Load Trained Model Pipeline with caching
@st.cache_resource
def load_pipeline():
    if os.path.exists("model_pipeline.pkl"):
        return joblib.load("model_pipeline.pkl")
    return None

model = load_pipeline()

# Session State
if "step" not in st.session_state:
    st.session_state.step = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# ----------------- PAGE 1: LOGIN -----------------
def render_login():
    st.markdown("<h2 style='text-align: center;'>⚡ VoltWise Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Data-Driven Electricity Budget & Advisory System</p>", unsafe_allow_html=True)
    st.write("")

    with st.container(border=True):
        st.subheader("Consumer Sign In")
        username_input = st.text_input("Consumer ID / Username", value="consumer_chennai_102")
        password_input = st.text_input("Password", type="password", value="securePass123")
        
        if st.button("Sign In 🔐", type="primary", use_container_width=True):
            if username_input.strip() and password_input.strip():
                st.session_state.username = username_input.strip()
                st.session_state.step = "audit"
                st.rerun()
            else:
                st.error("Please enter both ID and Password.")

# ----------------- PAGE 2: AUDIT FORM -----------------
def render_audit_form():
    c1, c2 = st.columns([4, 1])
    with c1:
        st.title("📋 Household Power & Budget Audit")
        st.caption(f"Consumer: **{st.session_state.username}**")
    with c2:
        if st.button("Log Out", use_container_width=True):
            st.session_state.clear()
            st.session_state.step = "login"
            st.rerun()

    with st.form("audit_form"):
        st.subheader("1. Region & Utility Details")
        r1, r2 = st.columns(2)
        with r1:
            city = st.selectbox("City", [
                "Chennai", "Mumbai", "New Delhi", "Ahmedabad", "Hyderabad", 
                "Kolkata", "Pune", "Noida", "Gurgaon", "Vadodara", "Ratnagiri", "Shimla"
            ])
            month = st.selectbox("Current Month", list(range(1, 13)), index=8)
        with r2:
            company = st.selectbox("Electricity Provider", [
                "Tata Power Company Ltd.", "Adani Power Ltd.", "Reliance Energy", 
                "CESC", "Torrent Power Ltd.", "JSW Energy Ltd.", "NTPC Pvt. Ltd."
            ])
            tariff_rate = st.number_input("Tariff Rate (₹/kWh)", min_value=5.0, max_value=12.0, value=8.37, step=0.05)

        st.divider()

        st.subheader("2. Financial Targets")
        f1, f2 = st.columns(2)
        with f1:
            prev_bill = st.number_input("Previous Month's Bill (₹)", min_value=100.0, max_value=30000.0, value=4200.0, step=50.0)
        with f2:
            monthly_budget = st.number_input("Target Monthly Budget (₹)", min_value=100.0, max_value=30000.0, value=3800.0, step=50.0)

        st.divider()

        st.subheader("3. Appliance Inventory & Runtimes")
        a1, a2, a3 = st.columns(3)
        with a1:
            fan = st.slider("Ceiling Fans (Units)", 1, 23, 14)
            ac = st.slider("Air Conditioners (Units)", 0, 4, 2)
        with a2:
            fridge = st.slider("Refrigerator (Daily Run Hours)", 15, 24, 22)
            tv = st.slider("Television (Daily Hours)", 2, 22, 12)
        with a3:
            monitor = st.slider("Computer/Monitor (Daily Hours)", 1, 12, 3)
            monthly_hours = st.slider("Total Monthly Aggregate Hours", 95, 926, 515)

        submit = st.form_submit_button("Run Advisory Model ➡️", type="primary", use_container_width=True)
        if submit:
            st.session_state.user_data = {
                "City": city, "Company": company, "Month": month, "TariffRate": tariff_rate,
                "Fan": fan, "Refrigerator": fridge, "AirConditioner": ac,
                "Television": tv, "Monitor": monitor, "MonthlyHours": monthly_hours,
                "prev_bill": prev_bill, "monthly_budget": monthly_budget
            }
            st.session_state.step = "dashboard"
            st.rerun()

# ----------------- PAGE 3: DASHBOARD & WHAT-IF -----------------
def render_dashboard():
    data = st.session_state.user_data

    # Top Navigation
    col_t1, col_t2, col_t3 = st.columns([5, 1.2, 1.2])
    with col_t1:
        st.title(f"📊 Energy Advisory Report: {data['City']}")
        st.caption(f"Consumer: **{st.session_state.username}** | Utility: **{data['Company']}** | Tariff: **₹{data['TariffRate']}/kWh**")
    with col_t2:
        if st.button("✏️ Edit Audit", use_container_width=True):
            st.session_state.step = "audit"
            st.rerun()
    with col_t3:
        if st.button("Log Out", use_container_width=True):
            st.session_state.clear()
            st.session_state.step = "login"
            st.rerun()

    st.divider()

    # Predict with ML Pipeline
    input_df = pd.DataFrame([{
        "Fan": data["Fan"],
        "Refrigerator": data["Refrigerator"],
        "AirConditioner": data["AirConditioner"],
        "Television": data["Television"],
        "Monitor": data["Monitor"],
        "Month": data["Month"],
        "City": data["City"],
        "Company": data["Company"],
        "MonthlyHours": data["MonthlyHours"],
        "TariffRate": data["TariffRate"]
    }])

    if model:
        predicted_bill = float(model.predict(input_df)[0])
    else:
        # Fallback estimation if model not detected
        predicted_bill = (data["MonthlyHours"] * 4.2 + data["AirConditioner"] * 800 + data["Fan"] * 45) * (data["TariffRate"] / 8.37)

    budget_diff = predicted_bill - data["monthly_budget"]
    prev_diff = predicted_bill - data["prev_bill"]

    # Health Score
    score = 100
    if data["AirConditioner"] > 1: score -= 20
    if data["MonthlyHours"] > 600: score -= 20
    if data["Television"] > 12: score -= 10
    if data["Monitor"] > 3: score -= 10
    health_score = max(0, min(100, score))

    # Top KPI Metrics
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Predicted Bill (ML)", f"₹{predicted_bill:,.2f}")
    k2.metric(
        "Budget Target",
        f"₹{data['monthly_budget']:,.2f}",
        delta=f"-₹{budget_diff:,.2f} Exceeded" if budget_diff > 0 else f"+₹{abs(budget_diff):,.2f} Under Budget",
        delta_color="inverse" if budget_diff > 0 else "normal"
    )
    k3.metric(
        "vs. Last Month",
        f"₹{data['prev_bill']:,.2f}",
        delta=f"+₹{prev_diff:,.2f}" if prev_diff > 0 else f"-₹{abs(prev_diff):,.2f}",
        delta_color="inverse" if prev_diff > 0 else "normal"
    )
    k4.metric("Electricity Health Score", f"{health_score} / 100")

    st.write("")

    if budget_diff > 0:
        st.error(f"🚨 **Budget Breach Alert:** Projected bill exceeds your budget by **₹{budget_diff:,.2f}** ({((budget_diff/data['monthly_budget'])*100):.1f}% over limit). Apply the reduction plan below.")
    else:
        st.success(f"🎉 **On Budget:** Your expected consumption is **₹{abs(budget_diff):,.2f} below** your ceiling.")

    # Two column: Chart + Recommendations
    col_chart, col_rec = st.columns([1, 1], gap="large")

    with col_chart:
        st.subheader("⚡ Approximate Appliance Load Share")
        breakdown_df = pd.DataFrame({
            "Component": ["Air Conditioners", "Fans", "Refrigerator", "TV & Monitors", "Base Grid Load"],
            "Cost (₹)": [
                data["AirConditioner"] * 820,
                data["Fan"] * 48,
                data["Refrigerator"] * 35,
                (data["Television"] * 25) + (data["Monitor"] * 30),
                data["MonthlyHours"] * 3.5
            ]
        }).set_index("Component")
        st.bar_chart(breakdown_df)

    with col_rec:
        st.subheader("💡 Recommended Actions to Recover Budget")
        actions = []
        if data["AirConditioner"] > 0:
            actions.append({"Appliance": "Air Conditioner", "Strategy": "Increase thermostat to 25°C & trim 1.5h daily usage", "Est. Savings": f"₹{data['AirConditioner']*320:,.0f}"})
        if data["Fan"] > 8:
            actions.append({"Appliance": "Ceiling Fans", "Strategy": "Switch off units in vacant rooms", "Est. Savings": f"₹{(data['Fan']-8)*24:,.0f}"})
        if data["Television"] > 8:
            actions.append({"Appliance": "Television", "Strategy": "Disable idle standby power consumption", "Est. Savings": f"₹{(data['Television']-8)*20:,.0f}"})
        if data["MonthlyHours"] > 500:
            actions.append({"Appliance": "Peak Usage", "Strategy": "Shift heavy iron & washing cycles to morning", "Est. Savings": f"₹{(data['MonthlyHours']-500)*3.5:,.0f}"})

        if actions:
            st.dataframe(pd.DataFrame(actions), use_container_width=True, hide_index=True)
        else:
            st.info("Current configuration operates within normal household parameters.")

    st.divider()

    # ----------------- GOAL #8: WHAT-IF SIMULATOR -----------------
    st.subheader("🧪 What-If Simulator")
    st.caption("Adjust prospective changes to test potential savings before making actual behavioral adjustments.")

    s1, s2, s3 = st.columns(3)
    with s1:
        sim_ac = st.slider("Simulate AC Units", 0, 4, data["AirConditioner"])
    with s2:
        sim_fan = st.slider("Simulate Fans", 1, 23, data["Fan"])
    with s3:
        sim_hours = st.slider("Simulate Monthly Hours", 95, 926, data["MonthlyHours"])

    sim_input = input_df.copy()
    sim_input["AirConditioner"] = sim_ac
    sim_input["Fan"] = sim_fan
    sim_input["MonthlyHours"] = sim_hours

    if model:
        sim_bill = float(model.predict(sim_input)[0])
    else:
        sim_bill = (sim_hours * 4.2 + sim_ac * 800 + sim_fan * 45) * (data["TariffRate"] / 8.37)

    bill_delta = predicted_bill - sim_bill
    st.info(f"💡 **Simulated Bill:** **₹{sim_bill:,.2f}** | **Net Monthly Difference:** {'🟢 Saves ₹' + f'{bill_delta:,.2f}' if bill_delta >= 0 else '🔴 Increases by ₹' + f'{abs(bill_delta):,.2f}'}")

# Router
if st.session_state.step == "login":
    render_login()
elif st.session_state.step == "audit":
    render_audit_form()
elif st.session_state.step == "dashboard":
    render_dashboard()
