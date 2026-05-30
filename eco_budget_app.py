import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
# -------------------------------
# Carbon factors per category
# (kg CO2e per ₹1)
# -------------------------------
CARBON_FACTORS = {
    "Transport": 0.25,
    "Food": 0.12,
    "Shopping": 0.15,
    "Bills": 0.18,
    "Entertainment": 0.08,
    "Travel": 0.30,
    "Other": 0.10,
}

CATEGORIES = list(CARBON_FACTORS.keys())

# -------------------------------
# Session state init
# -------------------------------
if "income" not in st.session_state:
    st.session_state.income = 50000.0

if "carbon_target" not in st.session_state:
    st.session_state.carbon_target = 300.0  # kg CO2e / month

if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount", "Carbon_kg", "Notes"]
    )

# -------------------------------
# Helper functions
# -------------------------------
def add_expense(exp_date: date, category: str, amount: float, notes: str = ""):
    factor = CARBON_FACTORS.get(category, CARBON_FACTORS["Other"])
    carbon = round(amount * factor, 2)

    new_row = pd.DataFrame(
        {
            "Date": [exp_date],
            "Category": [category],
            "Amount": [round(amount, 2)],
            "Carbon_kg": [carbon],
            "Notes": [notes],
        }
    )

    # Append to session_state table
    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_row], ignore_index=True
    )


def reset_expenses():
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount", "Carbon_kg", "Notes"]
    )


# -------- Chatbot-style suggestion helper --------
def get_suggestion_chatbot(message: str) -> str:
    """Very simple rule-based chatbot for suggestions."""
    text = message.lower().strip()
    if not text:
        return "Please type a question about money, spending or carbon. Example: 'How to reduce transport cost and carbon?'"

    if any(word in text for word in ["transport", "cab", "uber", "ola", "bike", "bus", "car", "travel"]):
        return (
            "Transport & travel usually create a lot of carbon.\n\n"
            "- Use public transport when possible (bus/metro)\n"
            "- Combine multiple small trips into one\n"
            "- Walk or cycle for short distances\n"
            "- Share rides with friends instead of going alone"
        )

    if any(word in text for word in ["food", "eat", "zomato", "swiggy", "restaurant", "meal"]):
        return (
            "Food impact can be reduced by:\n\n"
            "- Fewer online orders, more home-cooked meals\n"
            "- Choosing more plant-based meals (less red meat)\n"
            "- Avoiding food waste by planning portions\n"
            "- Buying local and seasonal items when possible"
        )

    if any(word in text for word in ["bill", "electricity", "current", "power", "ac", "fan", "light"]):
        return (
            "To lower electricity bills and carbon:\n\n"
            "- Set AC to 24–26°C instead of very low\n"
            "- Turn off lights and fans when leaving the room\n"
            "- Use LED bulbs and efficient appliances\n"
            "- Unplug chargers and devices when not in use"
        )

    if any(word in text for word in ["shopping", "clothes", "dress", "shirt", "buy", "online", "amazon", "flipkart"]):
        return (
            "Shopping generates carbon from manufacturing and shipping:\n\n"
            "- Buy only what you really need (avoid impulse buys)\n"
            "- Choose better quality items that last longer\n"
            "- Avoid fast fashion where possible\n"
            "- Wait 1–2 days before buying non-essential items"
        )

    if any(word in text for word in ["save money", "savings", "less spend", "budget"]):
        return (
            "To save money and carbon together:\n\n"
            "- Track where most of your money is going (transport, food, shopping)\n"
            "- Cut 10–20% from the least important category\n"
            "- Reduce high-cost, high-carbon habits like cabs and eating out\n"
            "- Set a monthly savings target and check it weekly"
        )

    if any(word in text for word in ["carbon", "footprint", "co2", "pollution"]):
        return (
            "To reduce your overall carbon footprint:\n\n"
            "- Focus on 3 areas: transport, energy at home, and food\n"
            "- Drive/fly less, use public transport more\n"
            "- Use electricity carefully (AC, lights, appliances)\n"
            "- Eat more plant-based meals and avoid waste"
        )

    # default generic answer
    return (
        "Good question! In general, you can lower both money spent and carbon by:\n\n"
        "- Reducing unnecessary travel\n"
        "- Cutting impulse online shopping\n"
        "- Being careful with electricity and AC use\n"
        "- Planning your monthly budget and tracking it weekly"
    )


# -------------------------------
# UI – layout & theme
# -------------------------------
st.set_page_config(
    page_title="EcoBudget – Carbon & Money Tracker",
    page_icon="🌍",
    layout="wide",
)

st.markdown(
    """
    <style>
    .big-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #555;
        margin-bottom: 1.2rem;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 999px;
        background: #e8f5e9;
        color: #256029;
        font-size: 0.78rem;
        margin-right: 6px;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">EcoBudget – Smart Money & Carbon Planner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Plan your monthly budget, track expenses, and see their carbon impact in one place.</div>',
    unsafe_allow_html=True,
)

# -------------------------------
# Sidebar controls
# -------------------------------
with st.sidebar:
    st.header("⚙ Settings")

    st.session_state.income = st.number_input(
        "Monthly Income (₹)",
        min_value=0.0,
        value=float(st.session_state.income),
        step=1000.0,
    )

    st.session_state.carbon_target = st.slider(
        "Monthly Carbon Target (kg CO₂e)",
        min_value=50.0,
        max_value=1000.0,
        value=float(st.session_state.carbon_target),
        step=10.0,
    )

    st.markdown("### 💡 Goal Style")
    goal_mode = st.radio(
        "",
        ["Balanced (money + carbon)", "Save Money", "Eco-first"],
        index=0,
    )

    st.markdown("---")
    if st.button("🧹 Clear all expenses"):
        reset_expenses()
        st.success("All expenses cleared.")

# -------------------------------
# Tabs
# -------------------------------
tab_overview, tab_add, tab_insights = st.tabs(
    ["📊 Overview", "➕ Add Expense", "🔍 Insights & Chatbot"]
)

# ----------------------------------------------------
# TAB: Overview
# ----------------------------------------------------
with tab_overview:
    df = st.session_state.expenses.copy()

    if df.empty:
        st.info("No expenses yet. Add your first expense in the **➕ Add Expense** tab.")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        df_sorted = df.sort_values("Date", ascending=False)

        # KPIs
        total_spent = df["Amount"].sum()
        total_carbon = df["Carbon_kg"].sum()
        income = st.session_state.income
        savings = max(0.0, income - total_spent)
        carbon_target = st.session_state.carbon_target

        spent_pct = (total_spent / income * 100) if income > 0 else 0
        carbon_pct = (total_carbon / carbon_target * 100) if carbon_target > 0 else 0
        savings_rate = (savings / income * 100) if income > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Monthly Income", f"₹{income:,.0f}")
        col2.metric("Total Spend", f"₹{total_spent:,.0f}", f"{spent_pct:.1f}% of income")
        col3.metric("Estimated Savings", f"₹{savings:,.0f}", f"{savings_rate:.1f}% saved")
        col4.metric("Total Carbon", f"{total_carbon:,.1f} kg CO₂e", f"{carbon_pct:.1f}% of target")

        # Progress bars
        st.markdown("### 📈 Budget & Carbon Progress")
        st.write("**Budget usage**")
        st.progress(min(1.0, spent_pct / 100 if income > 0 else 0.0))

        st.write("**Carbon usage**")
        st.progress(min(1.0, carbon_pct / 100 if carbon_target > 0 else 0.0))

        # Recent expenses table
        st.markdown("### 🧾 Recent Expenses")
        st.dataframe(
            df_sorted.head(15).assign(
                Date=lambda d: d["Date"].dt.date
            ),
            use_container_width=True,
        )

        # Category breakdown
        st.markdown("### 💸 Spend & Carbon by Category")
        cat_group = df.groupby("Category").agg(
            Total_Spend=("Amount", "sum"),
            Total_Carbon=("Carbon_kg", "sum"),
        ).reset_index()

        st.dataframe(
            cat_group.style.format(
                {"Total_Spend": "₹{:.0f}", "Total_Carbon": "{:.1f}"}
            ),
            use_container_width=True,
        )

        st.bar_chart(
            cat_group.set_index("Category")[["Total_Spend", "Total_Carbon"]],
            use_container_width=True,
        )

        # Eco score
        st.markdown("### 🏆 EcoBudget Score")

        money_score = max(0, 100 - spent_pct)
        carbon_score = max(0, 100 - carbon_pct)

        if goal_mode == "Balanced (money + carbon)":
            eco_score = (money_score * 0.5) + (carbon_score * 0.5)
        elif goal_mode == "Save Money":
            eco_score = (money_score * 0.7) + (carbon_score * 0.3)
        else:  # Eco-first
            eco_score = (money_score * 0.3) + (carbon_score * 0.7)

        eco_score = max(0, min(100, eco_score))

        st.metric("EcoBudget Score", f"{eco_score:.0f} / 100")

        if eco_score >= 80:
            st.success("🔥 Great job! You are doing very well on your budget and eco-goals.")
        elif eco_score >= 50:
            st.info("🙂 Not bad! Some tweaks in high-carbon or high-cost areas can boost your score.")
        else:
            st.warning("⚠ Your budget or carbon usage is on the higher side. Check Insights for improvement ideas.")

# ----------------------------------------------------
# TAB: Add Expense
# ----------------------------------------------------
with tab_add:
    st.subheader("➕ Add a New Expense")

    col_form_left, col_form_right = st.columns([2, 1])

    with col_form_left:
        with st.form("add_expense_form", clear_on_submit=True):
            d1, d2 = st.columns(2)
            with d1:
                exp_date = st.date_input("Date", value=date.today())
            with d2:
                category = st.selectbox("Category", CATEGORIES)

            amount = st.number_input(
                "Amount (₹)",
                min_value=1.0,
                value=500.0,
                step=50.0,
            )
            notes = st.text_input(
                "Notes (optional)",
                placeholder="Example: Ola ride, Zomato order, electricity bill..."
            )

            submitted = st.form_submit_button("Add Expense")

            if submitted:
                add_expense(exp_date, category, amount, notes)
                st.success("Expense added successfully!")
                # 🔁 Force full app rerun so Overview sees new data immediately
                st.rerun()

    with col_form_right:
        st.markdown("#### 📌 Current Overview")
        df2 = st.session_state.expenses.copy()
        if df2.empty:
            st.write("No expenses yet.")
        else:
            total_spent_now = df2["Amount"].sum()
            total_carbon_now = df2["Carbon_kg"].sum()
            st.write(f"**Total Spend:** ₹{total_spent_now:,.0f}")
            st.write(f"**Total Carbon:** {total_carbon_now:.1f} kg CO₂e")

        st.markdown("#### Category Carbon Factors")
        for cat, fac in CARBON_FACTORS.items():
            st.markdown(f"- **{cat}** → `{fac} kg CO₂e` per ₹1")

    st.markdown("### 📄 All Added Expenses")
    df3 = st.session_state.expenses.copy()
    if df3.empty:
        st.info("No expenses added yet.")
    else:
        df3["Date"] = pd.to_datetime(df3["Date"])
        st.dataframe(
            df3.sort_values("Date", ascending=False).assign(
                Date=lambda d: d["Date"].dt.date
            ),
            use_container_width=True,
        )

# ----------------------------------------------------
# TAB: Insights & Chatbot
# ----------------------------------------------------
with tab_insights:
    st.subheader("🔍 Insights & Chatbot Suggestions")

    df = st.session_state.expenses.copy()
    if df.empty:
        st.info("Add some expenses first to see insights.")
    else:
        df["Date"] = pd.to_datetime(df["Date"])
        max_date = df["Date"].max()
        cutoff_30 = max_date - timedelta(days=30)
        df_30 = df[df["Date"] >= cutoff_30]

        st.markdown("### 🕒 Last 30 Days Snapshot")
        if df_30.empty:
            st.write("No expenses in the last 30 days yet.")
        else:
            spent_30 = df_30["Amount"].sum()
            carbon_30 = df_30["Carbon_kg"].sum()
            st.write(f"- Spend (30 days): **₹{spent_30:,.0f}**")
            st.write(f"- Carbon (30 days): **{carbon_30:.1f} kg CO₂e**")

        # Top categories
        if not df.empty:
            cat_group_total = df.groupby("Category").agg(
                Total_Spend=("Amount", "sum"),
                Total_Carbon=("Carbon_kg", "sum"),
            ).reset_index()

            top_spend_cat = cat_group_total.sort_values("Total_Spend", ascending=False).iloc[0]
            top_carb_cat = cat_group_total.sort_values("Total_Carbon", ascending=False).iloc[0]

            st.markdown("### 🎯 Focus Areas")
            st.write(f"- Highest spend category: **{top_spend_cat['Category']}** (₹{top_spend_cat['Total_Spend']:.0f})")
            st.write(f"- Highest carbon category: **{top_carb_cat['Category']}** ({top_carb_cat['Total_Carbon']:.1f} kg CO₂e)")

    st.markdown("### 💬 Ask the Eco Chatbot")

    user_q = st.text_area(
        "Type your question (money + carbon):",
        placeholder="Example: How can I reduce transport cost and emissions?",
        height=100,
    )

    if st.button("Get suggestion"):
        reply = get_suggestion_chatbot(user_q)
        st.markdown("**Chatbot Suggestion:**")
        st.write(reply)

    with st.expander("See some general tips"):
        st.markdown('<span class="badge">Transport</span><span class="badge">Travel</span>', unsafe_allow_html=True)
        st.write("- Replace some cab rides with walking, cycling, or public transport.")
        st.write("- Combine multiple errands into one trip to reduce distance and fuel used.")

        st.markdown('<span class="badge">Food</span>', unsafe_allow_html=True)
        st.write("- Fewer food delivery orders, more home-cooked meals.")
        st.write("- Try a few plant-based meals per week.")

        st.markdown('<span class="badge">Bills</span>', unsafe_allow_html=True)
        st.write("- Keep AC at 24–26°C, use LED bulbs, and turn things off when not in use.")

        st.markdown('<span class="badge">Shopping</span>', unsafe_allow_html=True)
        st.write("- Delay non-essential purchases; ask yourself if you really need it.")
        st.write("- Prefer durable items that last longer.")
