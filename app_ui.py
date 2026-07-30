import streamlit as st
import pandas as pd
import requests
import json

# ─── Page Config ───
st.set_page_config(
    page_title="GharDaam — AI Property Valuation",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Constants ───
USD_TO_INR = 83.5

def format_inr(amount):
    """Format number in Indian Lakh/Crore system"""
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    else:
        return f"₹{amount:,.0f}"

def sqft_to_sqm(sqft):
    return sqft * 0.0929

# ─── Premium CSS ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700&display=swap');

    :root {
        --bg: #F7F8FC;
        --card: #FFFFFF;
        --text: #0B0F1A;
        --muted: #64748B;
        --accent: #4F46E5;
        --accent2: #7C3AED;
        --border: #E2E8F0;
        --success: #059669;
    }

    html, body, [class*="st-"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }
    
    h1, h2, h3, h4, h5, h6, label, p, span, div {
        color: var(--text) !important;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        border-radius: 20px;
        padding: 40px 48px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: 10%;
        width: 200px;
        height: 200px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #FFFFFF !important;
        letter-spacing: -1px;
        margin: 0;
        line-height: 1.1;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: rgba(255,255,255,0.85) !important;
        font-weight: 500;
        margin-top: 8px;
    }

    /* Glass Card */
    .glass-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        transition: box-shadow 0.3s ease;
    }
    .glass-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }

    .card-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text) !important;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Result Card */
    .result-card {
        background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%);
        border: 2px solid var(--accent);
        border-radius: 20px;
        padding: 36px 24px;
        text-align: center;
        margin-top: 16px;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.12);
    }
    .result-label {
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: var(--accent) !important;
        margin-bottom: 8px;
    }
    .result-price {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #3730A3 !important;
        letter-spacing: -1px;
        line-height: 1.15;
    }
    .result-usd {
        font-size: 1rem;
        color: var(--muted) !important;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Metric Pill */
    .metric-row {
        display: flex;
        gap: 12px;
        margin-top: 16px;
    }
    .metric-pill {
        flex: 1;
        background: #F1F5F9;
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
    }
    .metric-pill-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--muted) !important;
    }
    .metric-pill-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text) !important;
        margin-top: 2px;
    }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 16px 32px !important;
        border-radius: 14px !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
        letter-spacing: 0.5px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45) !important;
    }

    /* Inputs */
    .stTextInput input, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: var(--text) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1) !important;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        font-size: 0.8rem;
        color: var(--muted) !important;
        margin-top: 40px;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Hero Banner ───
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🏡 GharDaam</div>
    <div class="hero-sub">AI-Powered Property Valuation Engine • Predict house prices instantly in ₹ INR</div>
</div>
""", unsafe_allow_html=True)

# ─── Main Layout ───
col_input, col_result = st.columns([6, 5], gap="large")

with col_input:
    # Property Details Card
    st.markdown('<div class="glass-card"><div class="card-header">🏗️ Property Details</div></div>', unsafe_allow_html=True)
    
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        lot_area = st.number_input("🏞️ Plot Area (sq. ft)", min_value=500, max_value=50000, value=9000, step=250, 
                                   help="Total plot/lot area in square feet")
        gr_liv_area = st.number_input("📐 Carpet / Living Area (sq. ft)", min_value=300, max_value=8000, value=1800, step=100,
                                      help="Above-ground living area in square feet")
    with r1c2:
        year_built = st.number_input("📅 Year Built", min_value=1880, max_value=2026, value=2015, step=1,
                                     help="Year the house was originally constructed")
        garage_cars = st.selectbox("🚗 Parking / Garage Capacity", options=[0, 1, 2, 3, 4], index=2,
                                   help="Number of cars the garage can hold")

    # Quality Card
    st.markdown('<div class="glass-card"><div class="card-header">⭐ Quality & Condition Ratings</div></div>', unsafe_allow_html=True)
    
    q1, q2 = st.columns(2)
    with q1:
        overall_qual = st.slider("Build Quality (1-10)", 1, 10, 7, help="Overall material and finish quality")
    with q2:
        overall_cond = st.slider("Maintenance Condition (1-10)", 1, 10, 5, help="Overall condition / maintenance rating")

    # Predict Button
    st.markdown("")
    predict_btn = st.button("🔮 PREDICT PROPERTY VALUE")

with col_result:
    # API Config (Collapsed by default using expander)
    with st.expander("⚙️ API Configuration", expanded=False):
        api_endpoint = st.text_input("Model Endpoint", value="http://localhost:1235/invocations")
        st.caption("Docker: port 1235 | Kubernetes: port 8080")

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
            with st.spinner("🔄 Querying AI model..."):
                response = requests.post(api_endpoint, json=payload, timeout=8)
                
            if response.status_code == 200:
                result = response.json()
                price_usd = result["predictions"][0]
                price_inr = price_usd * USD_TO_INR
                
                # Price per sq ft
                price_per_sqft_inr = price_inr / gr_liv_area if gr_liv_area > 0 else 0
                house_age = 2026 - year_built
                area_sqm = sqft_to_sqm(gr_liv_area)
                
                # Main Result
                st.markdown(f"""
                <div class="result-card">
                    <div class="result-label">ESTIMATED PROPERTY VALUE</div>
                    <div class="result-price">{format_inr(price_inr)}</div>
                    <div class="result-usd">≈ ${price_usd:,.0f} USD</div>
                </div>
                """, unsafe_allow_html=True)

                # Metric Pills
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-pill">
                        <div class="metric-pill-label">Price / Sq.Ft</div>
                        <div class="metric-pill-value">₹{price_per_sqft_inr:,.0f}</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-pill-label">House Age</div>
                        <div class="metric-pill-value">{house_age} Yrs</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-pill-label">Area (m²)</div>
                        <div class="metric-pill-value">{area_sqm:.1f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Input Summary Table
                st.markdown("")
                st.markdown("##### 📋 Input Summary")
                summary_df = pd.DataFrame([{
                    "Plot Area": f"{lot_area:,} sq.ft",
                    "Living Area": f"{gr_liv_area:,} sq.ft",
                    "Year Built": str(year_built),
                    "Quality": f"{overall_qual}/10",
                    "Condition": f"{overall_cond}/10",
                    "Parking": f"{garage_cars} Cars"
                }])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)

            else:
                st.error(f"❌ API Error ({response.status_code}): {response.text[:200]}")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to the model API. Make sure Docker container is running:\n\n```bash\ndocker run -d -p 1235:1234 --name house-api house-price:v1\n```")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
    else:
        # Placeholder Info Card
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding: 48px 24px;">
            <div style="font-size: 3rem; margin-bottom: 12px;">🏡</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #0B0F1A !important;">Ready to Predict</div>
            <div style="font-size: 0.9rem; color: #64748B !important; margin-top: 8px;">
                Fill in the property details on the left and click<br><strong>PREDICT PROPERTY VALUE</strong> to get AI-estimated price in ₹ INR
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ───
st.markdown("""
<div class="footer-text">
    GharDaam v1.0 • Powered by MLflow + RandomForestRegressor • Model R² = 0.981
</div>
""", unsafe_allow_html=True)
