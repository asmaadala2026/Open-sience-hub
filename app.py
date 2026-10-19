import streamlit as st
import pandas as pd
import numpy as np

# 1. Force permanent Light Mode styling (White background, gray sidebar, clean typography)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }
    .stSidebar {
        background-color: #F3F4F6 !important;
        border-right: 1px solid #E5E7EB;
    }
    h1, h2, h3, h4, p, span, label, div, li {
        color: #1F2937 !important;
    }
    .stButton>button {
        background-color: #4F46E5 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 2. General Page Setup
st.set_page_config(page_title="Academic Python Open-Hub", layout="wide")

# 3. Sidebar Navigation Menu
sidebar = st.sidebar.radio("Navigation Menu:", ["🏠 Home & Open Science", "📊 JARS Data Analyzer", "📋 Open Science Auditor"])

# --- PAGE 1: HOME & OPEN SCIENCE ---
if sidebar == "🏠 Home & Open Science":
    st.title("🚀 Academic Python Open-Hub")
    st.subheader("An Open-Source Software Platform for Global Scientific Research")
    st.markdown(
        """
        Welcome to the practical platform designed to empower researchers and academics using Python. 
        This hub is fully built on free and open-source tools to promote **Open Science** and international reporting quality.
        
        ### 🎯 Platform Objectives:
        * **Enhance Transparency:** Free tools to host, share, and verify raw datasets.
        * **JARS Compliance:** Simplifying statistical reporting according to APA guidelines.
        * **Support Free Software:** Demonstrating Python's capability as a premium alternative to proprietary suites.
        """
    )

# --- PAGE 2: JARS DATA ANALYZER ---
elif sidebar == "📊 JARS Data Analyzer":
    st.title("📊 Automated Statistical Analyzer (JARS Compliant)")
    st.write("Upload your academic dataset from **Jamovi** (CSV format) or **SPSS** (.sav format) to generate instant descriptive statistics.")
    
    uploaded_file = st.file_uploader("Choose a file:", type=["csv", "sav"])
    
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.sav'):
            try:
                import pyreadstat
                df, meta = pyreadstat.read_sav(uploaded_file)
                st.success("SPSS (.sav) file detected and loaded successfully!")
            except ImportError:
                st.error("Missing dependency: pyreadstat. Please verify your requirements.txt file.")
        else:
            df = pd.read_csv(uploaded_file)
            st.success("CSV dataset loaded successfully!")
            
        st.write("📋 **Dataset Preview (First Rows):**", df.head())
        st.write("📈 **Descriptive Statistics Summary:**")
        st.write(df.describe())
    else:
        st.warning("Please upload a file to start the automated descriptive analysis.")

# --- PAGE 3: OPEN SCIENCE AUDITOR ---
elif sidebar == "📋 Open Science Auditor":
    st.title("📋 Open Science & JARS Compliance Auditor")
    st.write("Evaluate your research paper's transparency level before open-access journal submission.")
    
    st.markdown("### 📋 Verification Checklist:")
    q1 = st.checkbox("Is the analysis source code publicly available (e.g., on GitHub)?")
    q2 = st.checkbox("Are raw datasets deposited in a trusted open repository?")
    q3 = st.checkbox("Are descriptive statistical parameters fully documented?")
    
    if st.button("Generate Compliance Audit Report"):
        score = sum([q1, q2, q3])
        st.subheader("📊 Audit Result:")
        if score == 3:
            st.balloons()
            st.success("Excellent! Your study is fully compliant with JARS and Open Science core tenets. (3/3)")
        elif score > 0:
            st.warning(f"Good progress, but consider improving metadata transparency. Current score: ({score}/3)")
        else:
            st.error("Action Required: Your project lacks baseline open science transparency requirements. (0/3)")
