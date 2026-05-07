import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Infrastructure Credit Risk Model",
    page_icon="🏗️",
    layout="wide"
)

# ── Load artifacts ─────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return joblib.load('model/logistic_model.pkl')

@st.cache_resource
def load_features():
    return joblib.load('model/features.pkl')

@st.cache_resource
def load_odds():
    return joblib.load('model/odds_ratios.pkl')

@st.cache_resource
def load_cox():
    return joblib.load('model/cox_model.pkl')

@st.cache_data
def load_data():
    return pd.read_parquet('model/processed_data.parquet')

if not os.path.exists('model/logistic_model.pkl'):
    st.error("Model artifacts not found. Run all cells in `worldbankproj.ipynb` first, then relaunch this app.")
    st.stop()

pipe     = load_model()
FEATURES = load_features()
odds_df  = load_odds()
cph      = load_cox()
df       = load_data()

# ── Header ─────────────────────────────────────────────────────────────────
st.title("🏗️ Infrastructure Credit Risk Model")
st.caption(
    "Probability-of-default scoring for infrastructure projects · "
    "World Bank PPI Database (6,636 projects, 2000–2024)"
)

# ── Sidebar — project inputs ───────────────────────────────────────────────
st.sidebar.header("Project Parameters")

st.sidebar.subheader("Financials")
total_investment = st.sidebar.number_input("Total Investment (USD millions)", 0.0, 20000.0, 200.0, step=10.0)
contract_period  = st.sidebar.slider("Contract Period (years)", 1, 50, 25)
pct_private      = st.sidebar.slider("% Private Ownership", 0, 100, 100)
leverage         = st.sidebar.slider("Leverage Ratio (Debt Share)", 0.0, 1.0, 0.60, step=0.05)

st.sidebar.subheader("Project Type")
is_brownfield    = st.sidebar.checkbox("Brownfield / Divestiture")
is_high_risk_sec = st.sidebar.checkbox("High-Risk Sector (ICT / Transport)")
is_subsaharan    = st.sidebar.checkbox("Sub-Saharan Africa")

st.sidebar.subheader("Financing & Support")
has_direct       = st.sidebar.checkbox("Government Direct Support")
has_indirect     = st.sidebar.checkbox("Government Indirect Support")
has_multilateral = st.sidebar.checkbox("Multilateral Lender (IFC / ADB…)")
has_bilateral    = st.sidebar.checkbox("Bilateral Lender")
is_unsolicited   = st.sidebar.checkbox("Unsolicited Proposal")

# ── Build input vector ────────────────────────────────────────────────────
base_inputs = {
    'ContractPeriod':           contract_period,
    'PercentPrivate':           pct_private,
    'TotalInvestment':          total_investment,
    'PhysicalAssets':           total_investment * 0.85,
    'leverage_ratio':           leverage,
    'leverage_missing':         0,
    'has_direct_support':       int(has_direct),
    'has_indirect_support':     int(has_indirect),
    'has_multilateral':         int(has_multilateral),
    'has_bilateral':            int(has_bilateral),
    'is_unsolicited':           int(is_unsolicited),
    'is_subsaharan':            int(is_subsaharan),
    'is_brownfield_div':        int(is_brownfield),
    'is_high_risk_sector':      int(is_high_risk_sec),
    'TotalInvestment_missing':  0,
    'TotalDebtFunding_missing': 0,
}
input_vec = {f: base_inputs.get(f, 0) for f in FEATURES}
input_df  = pd.DataFrame([input_vec])[FEATURES]

prob = float(pipe.predict_proba(input_df)[0, 1])

if prob < 0.10:
    risk_label, risk_color, risk_emoji = "LOW RISK",    "green",  "🟢"
elif prob < 0.25:
    risk_label, risk_color, risk_emoji = "MEDIUM RISK", "orange", "🟡"
else:
    risk_label, risk_color, risk_emoji = "HIGH RISK",   "red",    "🔴"

# ── Tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Risk Score", "📈 Feature Importance", "🗄️ Project Explorer"])

# ── Tab 1: Risk Score ─────────────────────────────────────────────────────
with tab1:
    # ── Risk Score Card ────────────────────────────────────────────────────
    col_score, col_metrics = st.columns([1, 1])

    with col_score:
        st.markdown(f"## {risk_emoji} {risk_label}")
        st.metric("Probability of Distress", f"{prob:.1%}",
                  delta=f"{prob - 0.093:.1%}" if prob != 0.093 else None,
                  delta_color="inverse")

        # Risk scale indicator
        risk_ranges = {
            'Low\n(<10%)': 0.05,
            'Medium\n(10–25%)': 0.175,
            'High\n(>25%)': 0.35
        }
        fig_scale, ax_scale = plt.subplots(figsize=(8, 1.5))
        for i, (label, val) in enumerate(risk_ranges.items()):
            color = 'green' if i == 0 else ('orange' if i == 1 else 'red')
            ax_scale.barh([0], 0.15, left=i*0.33, height=0.3, color=color, alpha=0.7, edgecolor='black', linewidth=0.5)
            ax_scale.text(i*0.33 + 0.075, 0, label, ha='center', va='center', fontsize=9, fontweight='bold')
        marker_pos = prob
        ax_scale.axvline(marker_pos, color='black', linewidth=3, linestyle='-', label='This Project')
        ax_scale.set_xlim(-0.05, 1.05)
        ax_scale.set_ylim(-1, 1)
        ax_scale.set_xticks([])
        ax_scale.set_yticks([])
        ax_scale.spines['top'].set_visible(False)
        ax_scale.spines['right'].set_visible(False)
        ax_scale.spines['left'].set_visible(False)
        ax_scale.spines['bottom'].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig_scale, use_container_width=True)
        plt.close()

        st.caption("🟢 Low: <10% · 🟡 Medium: 10–25% · 🔴 High: >25%")

    with col_metrics:
        st.markdown("### Key Project Metrics")
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric("Contract Period", f"{contract_period} years")
            st.metric("Private Ownership", f"{pct_private}%")
        with metric_cols[1]:
            st.metric("Investment", f"${total_investment:,.0f}M")
            st.metric("Leverage", f"{leverage:.0%}")

    # ── Survival Curve ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### Project Longevity: Survival Probability Over Contract Life")
    st.markdown("*What % of similar projects remain active after N years from financial closure?*")

    survival_input = pd.DataFrame([{
        'ContractPeriod':      contract_period,
        'PercentPrivate':      pct_private,
        'TotalInvestment':     total_investment,
        'has_direct_support':  int(has_direct),
        'has_multilateral':    int(has_multilateral),
        'is_subsaharan':       int(is_subsaharan),
        'is_brownfield_div':   int(is_brownfield),
        'is_high_risk_sector': int(is_high_risk_sec),
        'leverage_ratio':      leverage,
    }])

    try:
        surv = cph.predict_survival_function(survival_input)

        fig, ax = plt.subplots(figsize=(12, 5))

        # Plot survival curve
        surv_data = surv.iloc[:, 0]
        ax.plot(surv_data.index, surv_data.values, color=risk_color, linewidth=3, label='This Project', marker='o', markersize=4)
        ax.fill_between(surv_data.index, surv_data.values, alpha=0.2, color=risk_color)

        # Add reference lines
        ax.axhline(0.5, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% survival')
        ax.axhline(0.75, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='75% survival')

        # Formatting
        ax.set_xlabel('Years since financial closure', fontsize=11, fontweight='bold')
        ax.set_ylabel('Probability project remains active', fontsize=11, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.2, linestyle=':')
        ax.legend(loc='upper right', fontsize=10)

        # Add annotations for key years
        if len(surv_data) > 0:
            mid_idx = len(surv_data) // 2
            end_idx = min(len(surv_data) - 1, int(contract_period))
            if end_idx > 0 and end_idx < len(surv_data):
                ax.annotate(f'{surv_data.iloc[end_idx]:.1%}',
                           xy=(surv_data.index[end_idx], surv_data.iloc[end_idx]),
                           xytext=(10, 10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor=risk_color, alpha=0.7, edgecolor='none'),
                           fontsize=10, fontweight='bold', color='white',
                           arrowprops=dict(arrowstyle='->', color=risk_color, lw=1.5))

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

        # Key insight
        final_survival = surv_data.iloc[-1] if len(surv_data) > 0 else np.nan
        st.success(f"📌 **Insight**: This project has a {final_survival:.1%} probability of remaining active through its full {contract_period}-year contract period.")

    except Exception as e:
        st.warning(f"⚠️ Survival analysis unavailable: {str(e)}")
        st.info("The Cox model may not have enough data for this project configuration.")

# ── Tab 2: Feature Importance ─────────────────────────────────────────────
with tab2:
    st.subheader("Credit Risk Factors — Logistic Regression Odds Ratios")
    st.caption("Odds Ratio > 1: increases default probability (red)  ·  < 1: protective factor (blue)")

    top_n = st.slider("Show top N features", 5, min(30, len(odds_df)), 15)
    top   = odds_df.head(top_n).copy()

    fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.38)))
    colors = ['tomato' if x > 1 else 'steelblue' for x in top['Odds Ratio']]
    ax.barh(top['Feature'], top['Odds Ratio'], color=colors)
    ax.axvline(1.0, color='black', linewidth=0.8, linestyle='--', label='Neutral (OR = 1)')
    ax.set_xlabel('Odds Ratio')
    ax.set_title('Risk Amplifiers (red) and Mitigants (blue)')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    with st.expander("Full coefficient table"):
        st.dataframe(
            odds_df.style.format({'Coefficient': '{:.3f}', 'Odds Ratio': '{:.3f}'}),
            use_container_width=True
        )

# ── Tab 3: Project Explorer ───────────────────────────────────────────────
with tab3:
    st.subheader("World Bank PPI Database Explorer")

    c1, c2, c3 = st.columns(3)
    with c1:
        status_filter = st.selectbox("Project status", ["All", "Distressed only", "Healthy only"])
    with c2:
        search_text = st.text_input("Search region / country", "")
    with c3:
        sector_opts = ["All"]
        if 'Primary sector' in df.columns:
            sector_opts += sorted(df['Primary sector'].dropna().unique().tolist())
        sector_filter = st.selectbox("Sector", sector_opts)

    view = df.copy()
    if status_filter == "Distressed only":
        view = view[view['distressed'] == 1]
    elif status_filter == "Healthy only":
        view = view[view['distressed'] == 0]
    if search_text:
        mask = pd.Series(False, index=view.index)
        for col in ['Region', 'Country']:
            if col in view.columns:
                mask |= view[col].str.contains(search_text, case=False, na=False)
        view = view[mask]
    if sector_filter != "All" and 'Primary sector' in view.columns:
        view = view[view['Primary sector'] == sector_filter]

    st.caption(f"Showing {min(len(view), 500):,} of {len(view):,} projects")

    display_cols = [c for c in ['Region', 'Country', 'Primary sector', 'Type of PPI',
                                'Financial closure year', 'Project status', 'distressed',
                                'TotalInvestment', 'ContractPeriod'] if c in view.columns]
    st.dataframe(
        view[display_cols].head(500),
        use_container_width=True,
        column_config={"distressed": st.column_config.CheckboxColumn("Distressed?")}
    )
