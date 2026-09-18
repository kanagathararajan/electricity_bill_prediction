import streamlit as st
import pandas as pd
import numpy as np

# Set layout dynamically based on current step
st.set_page_config(
    page_title="VoltWise | Smart Electricity Advisor",
    page_icon="⚡",
    layout="centered" if "step" in st.session_state and st.session_state.step == "login" else "wide"
)

# ----------------- SESSION STATE ROUTER -----------------
if "step" not in st.session_state:
    st.session_state.step = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# ----------------- STEP 1: AUTHENTICATION -----------------
def render_login():
    st.markdown("<h2 style='text-align: center;'>⚡ VoltWise Portal</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Smart Electricity Budget & Advisory System</p>", unsafe_allow_html=True)
    st.write("")

    with st.container(border=True):
        st.subheader("Sign In")
        username_input = st.text_input("Consumer ID / Username", value="consumer_chennai_102")
        password_input = st.text_input("Password", type="password", value="securePass123")
        
        col_btn, col_help = st.columns([1, 2])
        with col_btn:
            if st.button("Sign In 🔐", type="primary", use_container_width=True):
                if username_input.strip() and password_input.strip():
                    st.session_state.username = username_input.strip()
                    st.session_state.step = "audit"
                    st.rerun()
                else:
                    st.error("Please provide both Consumer ID and Password.")
        with col_help:
            st.caption("Demo credentials pre-filled. Click **Sign In** to proceed to the audit.")

# ----------------- STEP 2: HOUSEHOLD AUDIT FORM -----------------
def render_audit_form():
    c1, c2 = st.columns([4, 1])
    with c1:
        st.title("📋 Household Power & Appliance Audit")
        st.caption(f"Authenticated as: **{st.session_state.username}**")
    with c2:
        if st.button("Log Out", use_container_width=True):
            st.session_state.clear()
            st.session_state.step = "login"
            st.rerun()

    st.write("Please configure your regional electricity details and household inventory:")
    
    with st.form("energy_audit_form"):
        st.subheader("1. Regional & Provider Details")
        r1, r2 = st.columns(2)
        with r1:
            state = st.selectbox("State", ["Tamil Nadu", "Maharashtra", "Gujarat", "Delhi NCR", "Karnataka", "West Bengal"])
            city = st.selectbox("City", ["Chennai", "Mumbai", "New Delhi", "Ahmedabad", "Hyderabad", "Kolkata", "Pune", "Noida", "Vadodara"])
        with r2:
            company = st.selectbox("Electricity Board / Provider", [
                "TANGEDCO", "Tata Power Company Ltd.", "Adani Power Ltd.", 
                "Reliance Energy", "CESC", "Torrent Power Ltd."
            ])
            tariff_rate = st.number_input("Tariff Rate (₹ per kWh)", min_value=5.0, max_value=15.0, value=8.40, step=0.10)

        st.divider()

        st.subheader("2. Target Budget & Previous Consumption")
        f1, f2 = st.columns(2)
        with f1:
            prev_bill = st.number_input("Last Month's Billed Amount (₹)", min_value=100.0, max_value=30000.0, value=4200.0, step=50.0)
        with f2:
            monthly_budget = st.number_input("Your Desired Monthly Budget (₹)", min_value=100.0, max_value=30000.0, value=3500.0, step=50.0)

        st.divider()

        st.subheader("3. Appliance Inventory & Daily Usage")
        a1, a2, a3 = st.columns(3)
        with a1:
            fan = st.slider("Ceiling/Table Fans (Count)", 1, 20, 10)
            ac = st.slider("Air Conditioners (Units)", 0, 5, 2)
        with a2:
            fridge_hrs = st.slider("Refrigerator (Active Hours/Day)", 12, 24, 22)
            tv_hrs = st.slider("Television (Daily Hours)", 0, 18, 6)
        with a3:
            monitor_hrs = st.slider("Computer/Monitor (Daily Hours)", 0, 16, 4)
            monthly_hours = st.slider("Total Cumulative Grid Hours", 90, 950, 520)

        st.write("")
        submit_button = st.form_submit_button("Analyze Budget & View Recommendations ➡️", type="primary", use_container_width=True)

        if submit_button:
            st.session_state.user_data = {
                "state": state,
                "city": city,
                "company": company,
                "tariff_rate": tariff_rate,
                "prev_bill": prev_bill,
                "monthly_budget": monthly_budget,
                "fan": fan,
                "ac": ac,
                "fridge_hrs": fridge_hrs,
                "tv_hrs": tv_hrs,
                "monitor_hrs": monitor_hrs,
                "monthly_hours": monthly_hours
            }
            st.session_state.step = "dashboard"
            st.rerun()

# ----------------- STEP 3: ADVISORY DASHBOARD -----------------
def render_dashboard():
    data = st.session_state.user_data

    head_col, btn_col1, btn_col2 = st.columns([5, 1.2, 1.2])
    with head_col:
        st.title(f"📊 Energy Advisory Report: {data['city']}")
        st.caption(f"Consumer: **{st.session_state.username}** | Utility: **{data['company']}** | State: **{data['state']}**")
    with btn_col1:
        if st.button("✏️ Recalculate", use_container_width=True):
            st.session_state.step = "audit"
            st.rerun()
    with btn_col2:
        if st.button("Log Out", use_container_width=True):
            st.session_state.clear()
            st.session_state.step = "login"
            st.rerun()

    st.divider()

    rate_factor = data["tariff_rate"] / 8.37
    cost_ac = (data["ac"] * 820) * rate_factor
    cost_fan = (data["fan"] * 48) * rate_factor
    cost_fridge = (data["fridge_hrs"] * 35) * rate_factor
    cost_tv = (data["tv_hrs"] * 28) * rate_factor
    cost_monitor = (data["monitor_hrs"] * 32) * rate_factor
    base_cost = (data["monthly_hours"] * 3.6) * rate_factor

    predicted_bill = base_cost + cost_ac + cost_fan + cost_fridge + cost_tv + cost_monitor
    budget_deficit = predicted_bill - data["monthly_budget"]
    prev_bill_diff = predicted_bill - data["prev_bill"]

    score = 100
    if data["ac"] > 1: score -= 20
    if data["monthly_hours"] > 600: score -= 20
    if data["tv_hrs"] > 8: health_score = score - 10
    if data["monitor_hrs"] > 4: score -= 10
    health_score = max(0, min(100, score))

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Predicted Bill", f"₹{predicted_bill:,.2f}")
    m2.metric(
        "Budget Target",
        f"₹{data['monthly_budget']:,.2f}",
        delta=f"-₹{budget_deficit:,.2f} Over Budget" if budget_deficit > 0 else f"+₹{abs(budget_deficit):,.2f} Within Budget",
        delta_color="inverse" if budget_deficit > 0 else "normal"
    )
    m3.metric(
        "vs. Previous Month",
        f"₹{data['prev_bill']:,.2f}",
        delta=f"+₹{prev_bill_diff:,.2f}" if prev_bill_diff > 0 else f"-₹{abs(prev_bill_diff):,.2f}",
        delta_color="inverse" if prev_bill_diff > 0 else "normal"
    )
    m4.metric("Electricity Health Score", f"{health_score} / 100")

    st.write("")

    if budget_deficit > 0:
        st.error(f"🚨 **Budget Breach Alert:** Your projected bill exceeds your monthly budget by **₹{budget_deficit:,.2f}** ({((budget_deficit/data['monthly_budget'])*100):.1f}% over budget). Implement the action plan below to stay within budget.")
    else:
        st.success(f"🎉 **Within Budget:** Your current projected bill is **₹{abs(budget_deficit):,.2f} under** your set threshold.")

    col_chart, col_actions = st.columns([1, 1], gap="large")

    with col_chart:
        st.subheader("📊 Cost Distribution by Appliance")
        chart_df = pd.DataFrame({
            "Appliance": ["Air Conditioners", "Fans", "Refrigerator", "TV", "Computers/Monitors", "Baseline Grid"],
            "Estimated Bill (₹)": [cost_ac, cost_fan, cost_fridge, cost_tv, cost_monitor, base_cost]
        }).set_index("Appliance")
        st.bar_chart(chart_df)

    with col_actions:
        st.subheader("💡 Actionable Reduction Plan")
        recommendations = []

        if data["ac"] > 0:
            saving_ac = data["ac"] * 320 * rate_factor
            recommendations.append({
                "Appliance": "Air Conditioner",
                "Action Plan": "Set temperature to 24°C-26°C and enable sleep timer.",
                "Estimated Monthly Savings": f"₹{saving_ac:,.0f}"
            })
        if data["fan"] > 6:
            saving_fan = (data["fan"] - 6) * 25 * rate_factor
            recommendations.append({
                "Appliance": "Ceiling Fans",
                "Action Plan": "Turn off fans in unoccupied rooms and reduce run hours.",
                "Estimated Monthly Savings": f"₹{saving_fan:,.0f}"
            })
        if data["tv_hrs"] > 4:
            saving_tv = (data["tv_hrs"] - 4) * 20 * rate_factor
            recommendations.append({
                "Appliance": "Television",
                "Action Plan": "Turn off main wall switch when idle to eliminate standby draw.",
                "Estimated Monthly Savings": f"₹{saving_tv:,.0f}"
            })
        if data["monthly_hours"] > 500:
            saving_grid = (data["monthly_hours"] - 500) * 3.5 * rate_factor
            recommendations.append({
                "Appliance": "Peak Grid Hours",
                "Action Plan": "Schedule heavy washing and iron usage during off-peak morning hours.",
                "Estimated Monthly Savings": f"₹{saving_grid:,.0f}"
            })

        if recommendations:
            st.dataframe(pd.DataFrame(recommendations), use_container_width=True, hide_index=True)
        else:
            st.info("Your usage profile is already well within optimal thresholds.")

# ----------------- APP CONTROLLER -----------------
if st.session_state.step == "login":
    render_login()
elif st.session_state.step == "audit":
    render_audit_form()
elif st.session_state.step == "dashboard":
    render_dashboard()
