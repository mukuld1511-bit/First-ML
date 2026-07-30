import streamlit as st
import pandas as pd
import requests

# Page configuration
st.set_page_config(
    page_title="House Price Prediction System",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Light Minimal Bold Abstract Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap');

    /* Global Body styling for crisp Light Mode */
    html, body, [class*="st-"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* Ensure Streamlit Headings and Labels are Dark and Readable */
    h1, h2, h3, h4, h5, h6, label, p, span, div {
        color: #0F172A !important;
    }

    /* Abstract Cards */
    .abstract-card {
        background: #FFFFFF !important;
        border: 2px solid #0F172A !important;
        box-shadow: 6px 6px 0px #0F172A !important;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: #0F172A !important;
        line-height: 1.1;
        margin-bottom: 8px;
    }

    .hero-sub {
        font-size: 1.15rem;
        color: #475569 !important;
        font-weight: 600;
        margin-bottom: 32px;
    }

    /* Inputs Styling */
    .stTextInput input, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 2px solid #0F172A !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Primary Accent Button */
    .stButton > button {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        padding: 18px 32px !important;
        border-radius: 12px !important;
        border: 2px solid #0F172A !important;
        box-shadow: 5px 5px 0px #4338CA !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
        margin-top: 10px;
    }
    .stButton > button:hover {
        transform: translate(-2px, -2px) !important;
        box-shadow: 8px 8px 0px #4338CA !important;
        background-color: #1E1B4B !important;
        color: #FFFFFF !important;
    }

    /* Big Metric Display */
    .price-badge {
        background: #EEF2FF !important;
        border: 3px solid #4338CA !important;
        box-shadow: 8px 8px 0px #0F172A !important;
        border-radius: 20px;
        padding: 36px 20px;
        text-align: center;
        margin-top: 10px;
    }
    .price-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: #3730A3 !important;
        letter-spacing: -1px;
        line-height: 1.1;
        margin-top: 8px;
    }
    .price-label {
        font-size: 0.95rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: #4338CA !important;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="hero-title">House Price Prediction System</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Enter house specs below to generate AI price estimates</div>', unsafe_allow_html=True)

# Main Grid Layout
col_main, col_stats = st.columns([7, 5], gap="large")

with col_main:
    st.subheader("🎛️ House Features")
    
    # Input Sliders & Number Controls
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        lot_area = st.number_input("Lot Area (sq. ft)", min_value=500, max_value=50000, value=9000, step=500)
        gr_liv_area = st.number_input("Living Area (sq. ft)", min_value=300, max_value=8000, value=1900, step=100)
        year_built = st.slider("Year Built", 1880, 2026, 2010)

    with row1_c2:
        overall_qual = st.select_slider("Overall Quality Score", options=list(range(1, 11)), value=7)
        overall_cond = st.select_slider("Overall Condition Score", options=list(range(1, 11)), value=5)
        garage_cars = st.radio("Garage Capacity (Cars)", options=[0, 1, 2, 3, 4], index=2, horizontal=True)

    predict_btn = st.button("PREDICT HOUSE PRICE →")

with col_stats:
    st.subheader("⚙️ API Configuration")
    api_endpoint = st.text_input("Model Endpoint URL", value="http://localhost:1235/invocations")
    st.caption("Default Port: 1235 (Docker Container) | Port 8080 (Kubernetes)")

    if predict_btn:
        payload = {
            "dataframe_records": [
                {
                    "LotArea": lot_area,
                    "OverallQual": overall_qual,
                    "OverallCond": overall_cond,
                    "YearBuilt": year_built,
                    "GrLivArea": gr_liv_area,
                    "GarageCars": garage_cars
                }
            ]
        }

        try:
            with st.spinner("Connecting to model..."):
                response = requests.post(api_endpoint, json=payload, timeout=5)
                
            if response.status_code == 200:
                result = response.json()
                price = result["predictions"][0]
                
                st.markdown(f"""
                <div class="price-badge">
                    <div class="price-label">PREDICTED HOUSE PRICE</div>
                    <div class="price-value">${price:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"Endpoint Error ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API at {api_endpoint}. Please ensure Docker container or K8s is running.\n\nError: {e}")
    else:
        st.info("💡 Fill in the house features on the left and click **PREDICT HOUSE PRICE** to calculate valuation.")
