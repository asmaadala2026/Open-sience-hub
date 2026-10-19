import streamlit as st
import pandas as pd
import os
os.environ["STREAMLIT_PYARROW_DISABLE"] = "true"

# 1. Page Configuration
st.set_page_config(page_title="Academic Python Open-Hub", page_icon="🚀", layout="wide")

# 2. Sidebar Navigation
options = ["🏠 Home & Open Science", "📊 JARS Data Analyzer", "📋 Open Science Auditor"]
sidebar = st.sidebar.radio("Navigation:", options)

# --- PAGE 1: HOME ---
if sidebar == "🏠 Home & Open Science":
    st.title("🚀 Academic Python Open-Hub")
    st.subheader("An Open-Source Software Platform for Global Scientific Research")
    st.markdown("""
    Welcome to the practical platform designed to empower researchers and academics using **Python**.
    This hub is fully built on free and open-source tools to promote **Open Science** and international reporting quality.
    
    ### 🎯 Platform Objectives:
    * **Enhance Transparency:** Free tools to host, share, and verify raw datasets.
    * **JARS Compliance:** Simplifying statistical reporting according to APA guidelines.
    * **Support Free Software:** Demonstrating Python's capability as a premium alternative to proprietary suites.
    """)

# --- PAGE 2: JARS DATA ANALYZER ---
elif sidebar == "📊 JARS Data Analyzer":
    st.title("📊 Automated Statistical Analyzer (JARS Compliant)")
    st.write("Upload your dataset (CSV or Excel) to generate a standardized reporting summary instantly.")
    
    uploaded_file = st.file_uploader("Choose a file:", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("Dataset loaded successfully!")
            st.subheader("📋 Raw Data Preview:")
            st.dataframe(df.head())
            st.subheader("✨ Descriptives Summary (JARS-Quant Standards):")
            st.write(df.describe())
        except Exception as e:
            st.error(f"Error loading file: {e}")

# --- PAGE 3: OPEN SCIENCE AUDITOR ---
elif sidebar == "📋 Open Science Auditor":
    st.title("📋 Open Science & JARS Transparency Auditor")
    st.write("Evaluate your research workflow readiness:")
    
    q1 = st.checkbox("Have you shared your raw dataset in a public open repository?")
    q2 = st.checkbox("Did you explicitly report software versions (e.g., SPSS, Jamovi Cloud) in text?")
    q3 = st.checkbox("Does your dataset possess a registered permanent DOI?")
    
    if st.button("Calculate Transparency Score"):
        score = sum([q1, q2, q3])
        if score == 3:
            st.balloons()
            st.success("Excellent! Your workflow is 100% compliant with Open Science & JARS.")
        elif score == 2:
            st.warning("Very Good! Consider registering a DOI for international standard completeness.")
        else:
            st.error("Transparency workflow needs improvement. Consider open-sourcing materials.")
