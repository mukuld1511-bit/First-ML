import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="House Price Engine",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

USD_TO_INR = 83.5

def format_inr(amount):
    if amount >= 1_00_00_000:
        return f"₹ {amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹ {amount / 1_00_000:.2f} L"
    else:
        return f"₹ {amount:,.0f}"

# ─── Antigravity-Inspired Minimal CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --white: #FFFFFF;
        --off-white: #FAFAFA;
        --ghost: #F5F5F7;
        --border: #E8E8ED;
        --muted: #86868B;
        --text: #1D1D1F;
        --black: #000000;
        --accent: #0071E3;
    }

    /* ── Global Reset ── */
    html, body, [class*="st-"], .stApp,
    h1, h2, h3, h4, h5, h6, p, span, div, label, li {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text) !important;
    }
    .stApp {
        background: var(--white) !important;
    }

    /* ── Remove Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 3rem 4rem 2rem !important;
        max-width: 1200px !important;
    }

    /* ── Brand Header ── */
    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 4px;
    }
    .brand-dot {
        width: 10px;
        height: 10px;
        background: var(--black);
        border-radius: 2px;
    }
    .brand-name {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--muted) !important;
    }
    .hero-h {
        font-size: 3.6rem;
        font-weight: 700;
        letter-spacing: -2.5px;
        line-height: 1.05;
        color: var(--black) !important;
        margin: 16px 0 0 0;
    }
    .hero-p {
        font-size: 1.15rem;
        font-weight: 400;
        color: var(--muted) !important;
        margin: 12px 0 48px 0;
        line-height: 1.6;
    }

    /* ── Divider ── */
    .line {
        height: 1px;
        background: var(--border);
        margin: 32px 0;
    }

    /* ── Section Label ── */
    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: var(--muted) !important;
        margin-bottom: 20px;
    }

    /* ── Inputs ── */
    .stNumberInput input, .stTextInput input {
        background: var(--ghost) !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        background: var(--white) !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 0 0 4px rgba(0,0,0,0.04) !important;
    }

    /* ── Slider ── */
    .stSlider [data-baseweb="slider"] {
        margin-top: 0 !important;
    }

    /* ── Button ── */
    .stButton > button {
        background: var(--black) !important;
        color: var(--white) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 14px 28px !important;
        border-radius: 980px !important;
        border: none !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        box-shadow: none !important;
    }
    .stButton > button:hover {
        background: #333336 !important;
        transform: scale(1.01) !important;
    }
    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* ── Result ── */
    .result-wrap {
        padding: 48px 32px;
        text-align: center;
    }
    .result-eyebrow {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--muted) !important;
    }
    .result-num {
        font-family: 'Inter', sans-serif;
        font-size: 4.2rem;
        font-weight: 700;
        letter-spacing: -3px;
        color: var(--black) !important;
        line-height: 1.1;
        margin: 12px 0 4px 0;
    }
    .result-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 400;
        color: var(--muted) !important;
    }

    /* ── Stat Grid ── */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1px;
        background: var(--border);
        border-radius: 12px;
        overflow: hidden;
        margin-top: 32px;
    }
    .stat-cell {
        background: var(--ghost);
        padding: 20px;
        text-align: center;
    }
    .stat-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--black) !important;
    }
    .stat-key {
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        color: var(--muted) !important;
        margin-top: 4px;
    }

    /* ── Placeholder ── */
    .placeholder-box {
        border: 1.5px dashed var(--border);
        border-radius: 16px;
        padding: 64px 32px;
        text-align: center;
    }
    .placeholder-icon {
        font-size: 2rem;
        margin-bottom: 16px;
        opacity: 0.3;
    }
    .placeholder-text {
        font-size: 0.9rem;
        color: var(--muted) !important;
        line-height: 1.6;
    }

    /* ── Footer ── */
    .ft {
        text-align: center;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 1px;
        color: var(--muted) !important;
        margin-top: 64px;
        padding-bottom: 24px;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════
st.markdown("""
<div class="brand"><div class="brand-dot"></div><div class="brand-name">House Price Engine</div></div>
<div class="hero-h">Predict. Price.<br>Instantly.</div>
<div class="hero-p">AI-powered property valuation — trained on real estate data,<br>served via MLflow, priced in Indian Rupees.</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
#  LAYOUT
# ═══════════════════════════════════════
col_left, col_gap, col_right = st.columns([5, 0.5, 5])

with col_left:
    st.markdown('<div class="section-label">Property Specifications</div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        lot_area = st.number_input("Plot Area (sq ft)", min_value=500, max_value=50000, value=9000, step=250)
        year_built = st.number_input("Year Built", min_value=1880, max_value=2026, value=2015)
        overall_qual = st.slider("Build Quality", 1, 10, 7)
    with c2:
        gr_liv_area = st.number_input("Living Area (sq ft)", min_value=300, max_value=8000, value=1800, step=100)
        garage_cars = st.selectbox("Parking (Cars)", [0, 1, 2, 3, 4], index=2)
        overall_cond = st.slider("Condition", 1, 10, 5)

    st.markdown('<div class="line"></div>', unsafe_allow_html=True)
    predict_btn = st.button("Get Valuation →")

with col_right:
    # API config hidden in expander
    with st.expander("Endpoint", expanded=False):
        api_endpoint = st.text_input("URL", value="http://localhost:1235/invocations", label_visibility="collapsed")

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
            with st.spinner(""):
                resp = requests.post(api_endpoint, json=payload, timeout=8)
            if resp.status_code == 200:
                price_usd = resp.json()["predictions"][0]
                price_inr = price_usd * USD_TO_INR
                price_sqft = price_inr / gr_liv_area if gr_liv_area else 0
                house_age = 2026 - year_built
                area_sqm = gr_liv_area * 0.0929

                st.markdown(f"""
                <div class="result-wrap">
                    <div class="result-eyebrow">Estimated Value</div>
                    <div class="result-num">{format_inr(price_inr)}</div>
                    <div class="result-sub">${price_usd:,.0f} USD</div>
                </div>
                <div class="stat-grid">
                    <div class="stat-cell">
                        <div class="stat-val">₹{price_sqft:,.0f}</div>
                        <div class="stat-key">Per Sq Ft</div>
                    </div>
                    <div class="stat-cell">
                        <div class="stat-val">{house_age}y</div>
                        <div class="stat-key">Age</div>
                    </div>
                    <div class="stat-cell">
                        <div class="stat-val">{area_sqm:.0f}</div>
                        <div class="stat-key">Area m²</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Error {resp.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach model API. Run: `docker run -d -p 1235:1234 --name house-api house-price:v1`")
        except Exception as e:
            st.error(str(e))
    else:
        st.markdown("""
        <div class="placeholder-box">
            <div class="placeholder-icon">◼</div>
            <div class="placeholder-text">
                Configure property details on the left.<br>
                Click <strong>Get Valuation</strong> to generate<br>
                an AI-powered price estimate in ₹ INR.
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown('<div class="ft">HOUSE PRICE ENGINE · MLFLOW · RANDOM FOREST · R² 0.981</div>', unsafe_allow_html=True)
