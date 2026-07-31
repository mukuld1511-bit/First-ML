import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="House Price Engine",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

USD_TO_INR = 83.5

def format_inr(amount):
    if amount >= 1_00_00_000:
        return f"₹ {amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹ {amount / 1_00_00_000:.2f} L"
    else:
        return f"₹ {amount:,.0f}"

# ─── Premium Glassmorphism & Modern CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap');

    /* ── Global Canvas ── */
    html, body, [class*="st-"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    
    .block-container {
        padding: 2.5rem 3.5rem !important;
        max-width: 1250px !important;
    }

    /* ── Header Card ── */
    .header-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 20px;
        padding: 36px 40px;
        margin-bottom: 28px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        color: #FFFFFF !important;
    }
    .header-tag {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #38BDF8 !important;
        margin-bottom: 8px;
    }
    .header-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: -1px;
        color: #FFFFFF !important;
        line-height: 1.1;
    }
    .header-desc {
        font-size: 1rem;
        color: #94A3B8 !important;
        margin-top: 8px;
        font-weight: 400;
    }

    /* ── Container Cards ── */
    .glass-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    }
    .card-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A !important;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Input Styling ── */
    .stNumberInput input, .stTextInput input, div[data-baseweb="select"] > div {
        background: #F1F5F9 !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 10px !important;
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    /* ── Primary Action Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 16px 28px !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 20px -3px rgba(37, 99, 235, 0.4) !important;
    }
    .stButton > button p, .stButton > button span {
        color: #FFFFFF !important;
    }

    /* ── Result Card ── */
    .result-card {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
        border: 2px solid #3B82F6 !important;
        border-radius: 20px;
        padding: 40px 28px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.15);
    }
    .result-tag {
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #1D4ED8 !important;
    }
    .result-main {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.8rem;
        font-weight: 800;
        color: #1E40AF !important;
        letter-spacing: -1.5px;
        line-height: 1.1;
        margin: 8px 0;
    }
    .result-sub {
        font-size: 0.95rem;
        font-weight: 600;
        color: #475569 !important;
    }

    /* ── Metrics Row ── */
    .metrics-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-top: 20px;
    }
    .metric-card {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .metric-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A !important;
    }
    .metric-lbl {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748B !important;
        margin-top: 2px;
    }

    /* ── Empty State ── */
    .empty-state {
        background: #FFFFFF !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 20px;
        padding: 60px 32px;
        text-align: center;
    }
    .empty-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
    }
    .empty-text {
        font-size: 0.95rem;
        color: #64748B !important;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───
st.markdown("""
<div class="header-card">
    <div class="header-tag">AI REAL ESTATE ENGINE</div>
    <div class="header-title">House Price Prediction System</div>
    <div class="header-desc">Enter property dimensions and specs below to calculate instant AI market valuation in ₹ INR</div>
</div>
""", unsafe_allow_html=True)

# ─── MAIN LAYOUT ───
col_form, col_output = st.columns([6, 5], gap="large")

with col_form:
    st.markdown('<div class="glass-card"><div class="card-title">📐 Property Dimensions & Specs</div>', unsafe_allow_html=True)
    
    r1, r2 = st.columns(2)
    with r1:
        lot_area = st.number_input("Plot Area (sq ft)", min_value=500, max_value=50000, value=9000, step=250)
        gr_liv_area = st.number_input("Living Area (sq ft)", min_value=300, max_value=8000, value=1800, step=100)
        year_built = st.number_input("Year Built", min_value=1880, max_value=2026, value=2015)
    with r2:
        overall_qual = st.slider("Build Quality (1-10)", 1, 10, 7)
        overall_cond = st.slider("Condition (1-10)", 1, 10, 5)
        garage_cars = st.selectbox("Parking Capacity (Cars)", [0, 1, 2, 3, 4], index=2)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    predict_btn = st.button("Calculate Property Value →")

with col_output:
    with st.expander("⚙️ API Configuration", expanded=False):
        api_endpoint = st.text_input("Endpoint URL", value="http://localhost:1235/invocations")

    if predict_btn:
        payload = {
            "dataframe_records": [{
                "LotArea": lot_area,
                "OverallQual": overall_qual,
                "OverallCond": overall_cond,
                "YearBuilt": year_built,
                "GrLivArea": gr_liv_area,
                "GarageCars": garage_cars
            }]
        }
        try:
            with st.spinner("Connecting to model..."):
                resp = requests.post(api_endpoint, json=payload, timeout=8)
            if resp.status_code == 200:
                price_usd = resp.json()["predictions"][0]
                price_inr = price_usd * USD_TO_INR
                price_sqft = price_inr / gr_liv_area if gr_liv_area else 0
                house_age = 2026 - year_built
                area_sqm = gr_liv_area * 0.0929

                st.markdown(f"""
                <div class="result-card">
                    <div class="result-tag">ESTIMATED MARKET VALUATION</div>
                    <div class="result-main">{format_inr(price_inr)}</div>
                    <div class="result-sub">≈ ${price_usd:,.0f} USD</div>
                </div>
                <div class="metrics-row">
                    <div class="metric-card">
                        <div class="metric-val">₹{price_sqft:,.0f}</div>
                        <div class="metric-lbl">Per Sq Ft</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{house_age} Yrs</div>
                        <div class="metric-lbl">House Age</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{area_sqm:.0f} m²</div>
                        <div class="metric-lbl">Area Sqm</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach model API. Ensure container is running.")
        except Exception as e:
            st.error(str(e))
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🏠</div>
            <div style="font-weight:700; color:#0F172A; font-size:1.1rem; margin-bottom:4px;">Ready for Valuation</div>
            <div class="empty-text">Fill in the property specifications on the left and click <strong>Calculate Property Value</strong> to generate an instant estimate.</div>
        </div>
        """, unsafe_allow_html=True)
