from __future__ import annotations
import sklearn.utils.validation
import sklearn.utils
import factor_analyzer.factor_analyzer

_orig = sklearn.utils.validation.check_array

def _patched(*args, **kwargs):
    if 'force_all_finite' in kwargs:
        kwargs['ensure_all_finite'] = kwargs.pop('force_all_finite')
    return _orig(*args, **kwargs)

sklearn.utils.validation.check_array = _patched
sklearn.utils.check_array = _patched
factor_analyzer.factor_analyzer.check_array = _patched

import io
import hashlib
import re
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin as pg
import pyreadstat
import requests
import scipy.stats as stats
import streamlit as st
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
from semopy import Model, calc_stats

# --- Initialize Session State ---
for key in ['phase1_data', 'phase2_data', 'raw_data']:
    if key not in st.session_state:
        st.session_state[key] = None
if 'feedback_submitted' not in st.session_state:
    st.session_state['feedback_submitted'] = False
if 'lang' not in st.session_state:
    st.session_state.lang = 'العربية'

st.set_page_config(page_title="PsychoStat Pro · Psychometric Analysis", page_icon="💠", layout="wide", initial_sidebar_state="expanded")

# ------------------ Multi-Language Dictionary ------------------
translations = {
    'English': {
        'select_lang': '🌐 Select Language',
        'main_title': '💠 PsychoStat Pro',
        'subtitle': 'Explore the measurement quality of employee attitudes toward generative AI, with transparent samples, methods, and exportable results.',
        'developer': 'Platform Developer: Asmaa Dala',
        'tab1': '📊 1. Raw Data & Descriptives',
        'tab2': '🔍 2. Exploratory Factor Analysis (EFA)',
        'tab3': '📈 3. Confirmatory Factor Analysis (CFA)',
        'tab4': '📄 4. Analysis Report',
        'raw_processing': 'Raw Survey Data Processing',
        'raw_info': 'Upload your raw survey data (Excel/CSV) directly from Google Forms to automatically extract demographic tables and split data for EFA/CFA.',
        'upload_forms': 'Upload Google Forms Data (Excel/CSV)',
        'demo_summary': '1. Demographic Summary',
        'select_demo': 'Select Demographic Variables:',
        'normality_desc': '2. Descriptive Stats (Mean & SD)',
        'select_normality': 'Select Scale Items for Analysis:',
        'ready_split': 'Ready for Psychometric Analysis?',
        'split_btn': '✂️ Automatically Split Data for EFA & CFA (50/50)',
        'study_overview': 'Study Overview',
        'total_cases': 'Total available cases',
        'p1_cases': 'Phase 1 cases (EFA)',
        'p2_cases': 'Phase 2 cases (CFA)',
        'not_loaded': 'Not loaded',
        'case_study_title': '📖 Case Study: Employee Generative AI Attitude Scale (EGAIS) by Asmaa Dala',
        'case_study_desc': 'This validated scale is presented as a demo to illustrate the platform\'s capabilities. You can use this platform to analyze your own survey data with the same high precision 💯.',
        'case_study_intro': 'This scale (EGAIS) was developed specifically by researcher **Asmaa Dala** to measure employee attitudes toward generative AI in an actual work environment (an Algerian energy sector economic enterprise). Here are the actual robust results extracted by the platform:',
        'feedback_title': '💬 Feedback & Consultations',
        'feedback_desc': 'Share your thoughts on the platform or request a consultation.',
        'feedback_rating': 'How was your experience?',
        'fb_excellent': '😍 Excellent',
        'fb_good': '👍 Good & Useful',
        'fb_improve': '🤔 Needs Improvement',
        'feedback_text': 'Leave a comment or question here...',
        'feedback_submit': 'Send Feedback 🚀',
        'feedback_thanks': 'Thank you! Your feedback has been received. 😍',
        'mean_col': 'Mean',
        'sd_col': 'Std. Deviation',
        'run_efa': 'Run Exploratory Factor Analysis (EFA)',
        'run_cfa': 'Run Confirmatory Factor Analysis (CFA)',
        'factors_retain': 'Factors to retain',
        'num_cfa_factors': 'Number of CFA factors',
        'assign_items': 'Assign items to factors',
        'not_included': 'Not included',
        'factor': 'Factor'
    },
    'العربية': {
        'select_lang': '🌐 اختر اللغة',
        'main_title': '💠 PsychoStat Pro',
        'subtitle': 'استكشف جودة قياس اتجاهات الموظفين نحو الذكاء الاصطناعي التوليدي، مع عينات وأساليب ونتائج علمية دقيقة وقابلة للتصدير.',
        'developer': 'مطورة المنصة: أسماء دالة',
        'tab1': '📊 1. البيانات الخام والإحصاء الوصفي',
        'tab2': '🔍 2. التحليل الاستكشافي (EFA)',
        'tab3': '📈 3. التحليل التوكيدي (CFA)',
        'tab4': '📄 4. تقرير التحليل',
        'raw_processing': 'معالجة بيانات الاستبيان الخام',
        'raw_info': 'قم برفع بيانات الاستبيان الخام (Excel/CSV) مباشرة من نماذج جوجل لاستخراج الجداول الديموغرافية تلقائياً وتقسيم البيانات لمرحلتي EFA و CFA.',
        'upload_forms': 'رفع بيانات نماذج جوجل (Excel/CSV)',
        'demo_summary': '1. الملخص الديموغرافي',
        'select_demo': 'اختر المتغيرات الديموغرافية:',
        'normality_desc': '2. الإحصاء الوصفي',
        'select_normality': '📌 اختر فقرات المقياس للتحليل:',
        'ready_split': 'هل أنت جاهز للتحليل السيكومتري؟',
        'split_btn': '✂️ تقسيم البيانات تلقائياً لـ EFA و CFA (بنسبة 50/50)',
        'study_overview': 'نظرة عامة على الدراسة',
        'total_cases': 'إجمالي الحالات المتاحة',
        'p1_cases': 'حالات المرحلة 1 (EFA)',
        'p2_cases': 'حالات المرحلة 2 (CFA)',
        'not_loaded': 'لم يتم التحميل',
        'case_study_title': '📖 مثال تطبيقي: نتائج مقياس (EGAIS) للباحثة أسماء دالة',
        'case_study_desc': 'هذا المقياس المُحكّم معروض هنا كدراسة حالة حقيقية لتوضيح قدرة المنصة. يمكنك استخدام المنصة لتحليل بيانات استبيانك الخاص بنفس الدقة العالية 💯.',
        'case_study_intro': 'تم بناء وتطوير هذا المقياس (EGAIS) خصيصاً من قِبل الباحثة **أسماء دالة** لقياس اتجاهات الموظفين نحو الذكاء الاصطناعي التوليدي في بيئة العمل الفعلية (مؤسسة اقتصادية بقطاع الطاقة الجزائري). إليكِ النتائج الحقيقية والمبهرة التي استخرجتها المنصة:',
        'feedback_title': '💬 آراء ومقترحات الباحثين',
        'feedback_desc': 'يسعدنا سماع رأيك في المنصة أو ترك استشارتك.',
        'feedback_rating': 'كيف تقيم تجربتك؟',
        'fb_excellent': '😍 ممتازة جداً',
        'fb_good': '👍 جيدة ومفيدة',
        'fb_improve': '🤔 تحتاج بعض التحسين',
        'feedback_text': 'اكتب تعليقك أو استشارتك هنا...',
        'feedback_submit': 'إرسال 🚀',
        'feedback_thanks': 'شكراً لك! تم استلام رسالتك بنجاح. 😍',
        'mean_col': 'المتوسط الحسابي',
        'sd_col': 'الانحراف المعياري',
        'run_efa': 'إجراء التحليل العاملي الاستكشافي (EFA)',
        'run_cfa': 'إجراء التحليل العاملي التوكيدي (CFA)',
        'factors_retain': 'عدد العوامل المستخرجة',
        'num_cfa_factors': 'عدد عوامل التحليل التوكيدي',
        'assign_items': 'توزيع الفقرات على العوامل',
        'not_included': 'غير مدرج',
        'factor': 'العامل'
    },
    'Français': {
        'select_lang': '🌐 Choisir la langue',
        'main_title': '💠 PsychoStat Pro',
        'subtitle': 'Explorez la qualité de la mesure des attitudes des employés envers l’IA générative, avec des échantillons, méthodes et résultats exportables.',
        'developer': 'Développeuse: Asmaa Dala',
        'tab1': '📊 1. Données Brutes & Descriptives',
        'tab2': '🔍 2. Analyse Factorielle Exploratoire (EFA)',
        'tab3': '📈 3. Analyse Factorielle Confirmatoire (CFA)',
        'tab4': '📄 4. Rapport d\'Analyse',
        'raw_processing': 'Traitement des Données Brutes',
        'raw_info': 'Téléchargez vos données brutes (Excel/CSV) directement depuis Google Forms pour extraire automatiquement les tableaux démographiques et diviser les données pour EFA/CFA.',
        'upload_forms': 'Télécharger les Données Google Forms (Excel/CSV)',
        'demo_summary': '1. Résumé Démographique',
        'select_demo': 'Sélectionner les Variables Démographiques:',
        'normality_desc': '2. Statistiques Descriptives',
        'select_normality': '📌 Sélectionner les items de l\'échelle pour l\'analyse:',
        'ready_split': 'Prêt pour l\'Analyse Psychométrique ?',
        'split_btn': '✂️ Diviser Automatiquement les Données (50/50)',
        'study_overview': 'Aperçu de l\'Étude',
        'total_cases': 'Cas totaux disponibles',
        'p1_cases': 'Cas Phase 1 (EFA)',
        'p2_cases': 'Cas Phase 2 (CFA)',
        'not_loaded': 'Non chargé',
        'case_study_title': '📖 Étude de Cas: Échelle des Attitudes (EGAIS) par Asmaa Dala',
        'case_study_desc': 'Cette échelle validée est présentée comme démonstration. Vous pouvez utiliser cette plateforme pour analyser vos propres données avec la même précision 💯.',
        'case_study_intro': 'Cette échelle (EGAIS) a été développée spécifiquement par la chercheuse **Asmaa Dala** pour mesurer les attitudes des employés envers l\'IA générative dans un environnement de travail réel. Voici les résultats robustes extraits par la plateforme:',
        'feedback_title': '💬 Avis & Consultations',
        'feedback_desc': 'Partagez vos impressions sur la plateforme ou demandez une consultation.',
        'feedback_rating': 'Comment évaluez-vous votre expérience ?',
        'fb_excellent': '😍 Excellente',
        'fb_good': '👍 Bonne et Utile',
        'fb_improve': '🤔 Nécessite des améliorations',
        'feedback_text': 'Laissez un commentaire ou une question ici...',
        'feedback_submit': 'Envoyer 🚀',
        'feedback_thanks': 'Merci ! Votre message a été reçu avec succès. 😍',
        'mean_col': 'Moyenne',
        'sd_col': 'Écart-type',
        'run_efa': 'Lancer l\'Analyse Exploratoire (EFA)',
        'run_cfa': 'Lancer l\'Analyse Confirmatoire (CFA)',
        'factors_retain': 'Nombre de facteurs à retenir',
        'num_cfa_factors': 'Nombre de facteurs CFA',
        'assign_items': 'Assigner les items aux facteurs',
        'not_included': 'Non inclus',
        'factor': 'Facteur'
    }
}

# --- Custom Global Styles (UI Improvements) ---
st.markdown("""
    <style>
    /* Prominent Colorful Buttons */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child, div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important; 
        border-color: #3b82f6 !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
    }
    /* Case Study Card */
    .case-study-card {
        background: linear-gradient(to right, #f0f9ff, #e0f2fe);
        border: 2px solid #bae6fd; border-right: 8px solid #0284c7; 
        border-radius: 12px; padding: 25px; margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.15);
    }
    .case-study-card h3 { color: #0c4a6e; margin-top: 0; font-weight: 800; font-size: 1.3rem; }
    .case-study-card p { color: #0369a1; font-size: 1rem; font-weight: 500; }
    /* Metric boxes */
    [data-testid="stMetric"] { background: #fff; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    /* Headers */
    h1, h2, h3, h4 { color: #17324d; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# Sidebar Language Selection
selected_language = st.sidebar.selectbox(
    translations[st.session_state.lang]['select_lang'],
    ['العربية', 'English', 'Français'],
    index=['العربية', 'English', 'Français'].index(st.session_state.lang)
)
st.session_state.lang = selected_language
lang_dict = translations[st.session_state.lang]

# --- Helper Functions ---
SUPPORTED_TYPES = ["sav", "xlsx", "xls", "csv"]
TARGET_N_PER_PHASE = 150
PHASE_LABELS = {"phase1": "Phase 1 · EFA", "phase2": "Phase 2 · CFA"}

def as_numeric_items(data: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    return data.loc[:, items].apply(pd.to_numeric, errors="coerce")

def efa_result(data: pd.DataFrame, items: list[str], factor_count: int, rotation: str) -> dict[str, Any]:
    complete = as_numeric_items(data, items).dropna(axis=0, how="any")
    try:
        kmo_all, kmo_model = calculate_kmo(complete)
        bartlett_chi2, bartlett_p = calculate_bartlett_sphericity(complete)
    except Exception:
        kmo_all, kmo_model, bartlett_chi2, bartlett_p = np.full(len(items), np.nan), np.nan, np.nan, np.nan
    fa = FactorAnalyzer(n_factors=factor_count, rotation=rotation, method='principal')
    fa.fit(complete)
    loadings = pd.DataFrame(fa.loadings_, index=items, columns=[f"{lang_dict.get('factor')} {i+1}" for i in range(factor_count)])
    ev, _ = fa.get_eigenvalues()
    return {"n_complete": len(complete), "kmo": kmo_model, "kmo_items": pd.Series(kmo_all, index=items), "bartlett_chi2": bartlett_chi2, "bartlett_p": bartlett_p, "method": "PCA", "rotation": rotation, "factor_count": factor_count, "loadings": loadings, "eigenvalues": pd.DataFrame({"Component": range(1, len(ev) + 1), "Eigenvalue": ev})}

def build_cfa_specification(factor_assignments: dict[str, list[str]]) -> dict[str, Any]:
    used_items = [item for factor_items in factor_assignments.values() for item in factor_items]
    aliases, alias_to_item = {}, {}
    for item in used_items:
        base = f"item_{re.sub(r'[^A-Za-z0-9_]+', '_', str(item)).strip('_') or 'response'}"
        alias = base
        suffix = 2
        while alias in alias_to_item:
            alias = f"{base}_{suffix}"
            suffix += 1
        aliases[item] = alias
        alias_to_item[alias] = str(item)
    semopy_lines, display_lines, factor_aliases = [], [], {}
    for index, (factor, factor_items) in enumerate(factor_assignments.items(), start=1):
        factor_alias = f"F{index}"
        factor_aliases[factor_alias] = factor
        semopy_lines.append(f"{factor_alias} =~ " + " + ".join(aliases[item] for item in factor_items))
        display_lines.append(f"{factor} =~ " + " + ".join(map(str, factor_items)))
    return {"items": used_items, "aliases": aliases, "alias_to_item": alias_to_item, "factor_aliases": factor_aliases, "engine_syntax": "\n".join(semopy_lines), "display_syntax": "\n".join(display_lines)}

def cfa_result(data: pd.DataFrame, factor_assignments: dict[str, list[str]], specification: dict[str, Any]) -> dict[str, Any]:
    items = specification["items"]
    complete = as_numeric_items(data, items).dropna(axis=0, how="any")
    renamed = complete.rename(columns=specification["aliases"])
    model = Model(specification["engine_syntax"])
    fit_result = model.fit(renamed, obj="MLW")
    fit_table = calc_stats(model).iloc[0]
    fit_values = {name: float(fit_table.get(name, np.nan)) if pd.notna(fit_table.get(name, np.nan)) else np.nan for name in ["chi2", "DoF", "chi2 p-value", "CFI", "TLI", "RMSEA", "AIC", "BIC", "LogLik"]}
    parameters = model.inspect(std_est=True)
    for column in ("Estimate", "Est. Std", "Std. Err", "z-value", "p-value"):
        if column in parameters.columns: parameters[column] = pd.to_numeric(parameters[column], errors="coerce")
    for column in ("lval", "rval"):
        parameters[column] = parameters[column].replace({**specification["alias_to_item"], **specification["factor_aliases"]})
    parameters = parameters.rename(columns={"lval": "Left", "op": "Operator", "rval": "Right", "Estimate": "Estimate", "Est. Std": "Standardized estimate", "Std. Err": "SE", "z-value": "z", "p-value": "p"})
    return {"n_complete": int(len(complete)), "item_count": len(items), "factor_count": len(factor_assignments), "fit": fit_values, "parameters": parameters, "specification": specification, "estimator": "MLW", "assumption": "Continuous"}


# --- Modern Header ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); padding: 45px 30px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4); margin-bottom: 30px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 48px; font-weight: 900; letter-spacing: 1px;">{lang_dict.get('main_title')}</h1>
        <p style="font-size: 18px; margin: 15px auto 0 auto; max-width: 800px; opacity: 0.95;">{lang_dict.get('subtitle')}</p>
        <div style="margin-top: 25px; display: inline-block; background: rgba(255, 255, 255, 0.15); padding: 8px 24px; border-radius: 50px; font-size: 15px; font-weight: 600; border: 1px solid rgba(255,255,255,0.2);">
            👩‍💻 {lang_dict.get('developer')}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Prominent "Scale Guide" Integration (Stunning EGAIS Tables) ---
st.markdown(f"""
    <div class="case-study-card">
        <h3>{lang_dict.get('case_study_title')}</h3>
        <p>{lang_dict.get('case_study_desc')}</p>
    </div>
""", unsafe_allow_html=True)
with st.expander("🔍 " + lang_dict.get('select_lang') + " / عرض تفاصيل ونتائج المقياس 📊", expanded=False):
    st.markdown(lang_dict.get('case_study_intro'))
    
    st.markdown("##### 📊 1. التحليل الاستكشافي (EFA) - القوة التفسيرية")
    efa_demo_df = pd.DataFrame({
        "الأبعاد المستخرجة": ["القلق من الذكاء الاصطناعي", "الفعالية المدركة"],
        "عدد الفقرات": [12, 11],
        "التباين المفسر (Variance)": ["67.045%", "-"]
    })
    st.dataframe(efa_demo_df, hide_index=True, use_container_width=True)

    st.markdown("##### 📈 2. التحليل التوكيدي (CFA) - الثبات ومؤشرات المطابقة")
    cfa_demo_df = pd.DataFrame({
        "المؤشر (Metric)": ["الثبات المركب (CR)", "التباين المستخرج (AVE)", "كاي مربع (χ²)", "درجات الحرية (df)", "CFI", "TLI", "RMSEA"],
        "النتيجة (Value)": ["0.964", "0.562", "402.09", "189", "0.911", "0.901", "0.087"],
        "التقييم (Status)": ["ممتاز ✅", "جيد جداً ✅", "-", "-", "مطابق ✅", "مطابق ✅", "مقبول ✅"]
    })
    st.dataframe(cfa_demo_df.style.set_properties(**{'background-color': '#f8fafc'}), hide_index=True, use_container_width=True)
    st.success("💯 تُثبت هذه النتائج القوية الدقة العالية لمقياس (EGAIS) وكفاءة منصة PsychoStat Pro.")

# --- Sidebar: Simplified (Only Language & Feedback) ---
with st.sidebar:
    st.markdown("---")
    st.markdown(f"### {lang_dict.get('feedback_title')}")
    st.caption(lang_dict.get('feedback_desc'))
    
    if not st.session_state['feedback_submitted']:
        with st.form("feedback_form"):
            st.radio(lang_dict.get('feedback_rating'), [lang_dict.get('fb_excellent'), lang_dict.get('fb_good'), lang_dict.get('fb_improve')])
            st.text_area(lang_dict.get('feedback_text'), height=80)
            submitted = st.form_submit_button(lang_dict.get('feedback_submit'))
            if submitted:
                st.session_state['feedback_submitted'] = True
                st.rerun()
    else:
        st.success(lang_dict.get('feedback_thanks'))
        if st.button("إرسال رسالة أخرى"):
            st.session_state['feedback_submitted'] = False
            st.rerun()

available_data = [d for d in (st.session_state['phase1_data'], st.session_state['phase2_data'], st.session_state['raw_data']) if d is not None]
selected_items = []
if available_data:
    common_columns = set(available_data[0].columns)
    for data in available_data[1:]: common_columns &= set(data.columns)
    numeric_items = [col for col in available_data[0].select_dtypes(include=[np.number]).columns if col in common_columns and not any(kw in str(col).lower() for kw in ['id', 'case', 'total', 'gender'])]
    if numeric_items:
        default_items = [col for col in numeric_items if str(col).lower().startswith('s') and str(col).lower() not in ["some", "some1", "some2"]]
        if not default_items: default_items = numeric_items[:min(10, len(numeric_items))]
        # Global multiselect above tabs
        st.markdown("---")
        selected_items = st.multiselect(lang_dict.get('select_normality'), options=numeric_items, default=default_items)

tab_desc, tab_efa, tab_cfa, tab_report = st.tabs([lang_dict.get('tab1'), lang_dict.get('tab2'), lang_dict.get('tab3'), lang_dict.get('tab4')])

# ==========================================
# TAB 1: DESCRIPTIVE STATS & RAW DATA
# ==========================================
with tab_desc:
    st.markdown(f"#### {lang_dict.get('raw_processing')}")
    st.info(lang_dict.get('raw_info'))
    raw_file = st.file_uploader(lang_dict.get('upload_forms'), type=["csv", "xlsx", "xls"])
    
    if raw_file is not None:
        df_raw = pd.read_csv(raw_file) if raw_file.name.endswith('.csv') else pd.read_excel(raw_file)
        st.session_state['raw_data'] = df_raw
        st.success(f"✅ Data loaded successfully! Total responses: **{len(df_raw)}**")
        
        # Demographic Summary (Full Width)
        st.markdown("---")
        st.markdown(f"**{lang_dict.get('demo_summary')}**")
        demo_cols = st.multiselect(lang_dict.get('select_demo'), df_raw.columns, key="demo_cols")
        if demo_cols:
            for col in demo_cols:
                freq_df = df_raw[col].value_counts().reset_index()
                freq_df.columns = [col, 'Frequency']
                freq_df['Percentage (%)'] = (freq_df['Frequency'] / len(df_raw) * 100).round(2)
                st.write(f"**{col}**")
                st.dataframe(freq_df, use_container_width=True)
                
        # Descriptive Stats (Full Width, Mean & SD only)
        st.markdown("---")
        st.markdown(f"**{lang_dict.get('normality_desc')}**")
        if selected_items:
            desc_df = df_raw[selected_items].describe().T[['mean', 'std']].round(3)
            # Translated columns
            desc_df.rename(columns={'mean': lang_dict.get('mean_col'), 'std': lang_dict.get('sd_col')}, inplace=True)
            st.dataframe(desc_df, use_container_width=True)
                
        # Data Splitting Action
        st.markdown("---")
        st.markdown(f"#### {lang_dict.get('ready_split')}")
        if st.button(lang_dict.get('split_btn')):
            df_shuffled = df_raw.sample(frac=1, random_state=42).reset_index(drop=True)
            split_idx = len(df_shuffled) // 2
            st.session_state['phase1_data'] = df_shuffled.iloc[:split_idx]
            st.session_state['phase2_data'] = df_shuffled.iloc[split_idx:]
            st.success(f"Data successfully split! {split_idx} routed to EFA tab, {len(df_shuffled)-split_idx} routed to CFA tab. Proceed to the next tabs.")

    # Study Overview Summary
    st.markdown("---")
    st.markdown(f"#### {lang_dict.get('study_overview')}")
    phase_cols = st.columns(3)
    p1_len = len(st.session_state['phase1_data']) if st.session_state['phase1_data'] is not None else 0
    p2_len = len(st.session_state['phase2_data']) if st.session_state['phase2_data'] is not None else 0
    phase_cols[0].metric(lang_dict.get('total_cases'), p1_len + p2_len)
    phase_cols[1].metric(lang_dict.get('p1_cases'), p1_len if p1_len > 0 else lang_dict.get('not_loaded'))
    phase_cols[2].metric(lang_dict.get('p2_cases'), p2_len if p2_len > 0 else lang_dict.get('not_loaded'))

# ==========================================
# TAB 2: EXPLORATORY FACTOR ANALYSIS (EFA)
# ==========================================
with tab_efa:
    if st.session_state['phase1_data'] is not None and selected_items:
        controls = st.columns(2)
        with controls[0]: factor_count = st.number_input(lang_dict.get('factors_retain'), min_value=1, value=2, step=1)
        with controls[1]: rotation = st.selectbox("Rotation", ["varimax"])
        if st.button(lang_dict.get('run_efa')):
            try:
                efa_output = efa_result(st.session_state['phase1_data'], selected_items, int(factor_count), rotation)
                
                # Metrics
                metrics = st.columns(4)
                metrics[2].metric("Bartlett χ²", f"{efa_output['bartlett_chi2']:.2f}") 
                metrics[3].metric("Bartlett p", f"{efa_output['bartlett_p']:.4g}")
                
                # Loadings
                st.markdown("#### Factor loadings")
                st.dataframe(efa_output["loadings"].style.format("{:.3f}"), width="stretch")
                
                # Reliability & KMO
                st.markdown("#### Item-level KMO")
                st.dataframe(efa_output["kmo_items"].rename_axis("Item").reset_index().style.format({"KMO": "{:.3f}"}), width="stretch", hide_index=True)
                
            except Exception as e:
                st.error(f"EFA Error: {str(e)}")

# ==========================================
# TAB 3: CONFIRMATORY FACTOR ANALYSIS (CFA)
# ==========================================
with tab_cfa:
    if st.session_state['phase2_data'] is not None and selected_items:
        cfa_factor_count = st.number_input(lang_dict.get('num_cfa_factors'), min_value=1, value=2, step=1, key="cfa_factors")
        
        # Simple Assignment UI
        st.markdown(f"#### {lang_dict.get('assign_items')}")
        cfa_factor_labels = [f"{lang_dict.get('factor')} {i+1}" for i in range(cfa_factor_count)]
        select_options = [lang_dict.get('not_included')] + cfa_factor_labels
        assignment_columns = st.columns(2)
        assignment_by_item = {}
        for i, item in enumerate(selected_items):
            with assignment_columns[i % 2]:
                assignment_by_item[item] = st.selectbox(str(item), options=select_options, key=f"cfa_{item}")
                
        factor_assignments = {factor: [item for item, assigned_factor in assignment_by_item.items() if assigned_factor == factor] for factor in cfa_factor_labels}
        
        if st.button(lang_dict.get('run_cfa')):
            try:
                cfa_spec = build_cfa_specification(factor_assignments)
                cfa_out = cfa_result(st.session_state['phase2_data'], factor_assignments, cfa_spec)
                
                st.markdown("#### Model fit")
                fit_vals = cfa_out["fit"]
                f_cols = st.columns(4)
                f_cols[0].metric("CFI", f"{fit_vals['CFI']:.3f}")
                f_cols[1].metric("TLI", f"{fit_vals['TLI']:.3f}")
                f_cols[2].metric("RMSEA", f"{fit_vals['RMSEA']:.3f}")
                f_cols[3].metric("χ² (df)", f"{fit_vals['chi2']:.2f} ({fit_vals['DoF']:.0f})")
                
                st.markdown("#### Parameter estimates")
                st.dataframe(cfa_out["parameters"].style.format({"Estimate": "{:.3f}", "Standardized estimate": "{:.3f}", "SE": "{:.3f}", "z": "{:.3f}", "p": "{:.4g}"}, na_rep="—"), width="stretch", hide_index=True)
            except Exception as e:
                st.error(f"CFA Error: {str(e)}")

# ==========================================
# TAB 4: ANALYSIS REPORT
# ==========================================
with tab_report:
    st.info("Analysis reports will be available here after running EFA and CFA in the previous tabs.")
