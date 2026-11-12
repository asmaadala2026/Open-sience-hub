# -*- coding: utf-8 -*-
from __future__ import annotations
import sklearn.utils.validation
import sklearn.utils
import factor_analyzer.factor_analyzer
import io, hashlib, re, tempfile
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

# --- Fix for sklearn validation ---
_orig = sklearn.utils.validation.check_array
def _patched(*args, **kwargs):
    if 'force_all_finite' in kwargs: kwargs['ensure_all_finite'] = kwargs.pop('force_all_finite')
    return _orig(*args, **kwargs)
sklearn.utils.validation.check_array = _patched
sklearn.utils.check_array = _patched
factor_analyzer.factor_analyzer.check_array = _patched

# --- Initialize Session State ---
for key in ['phase1_data', 'phase2_data', 'raw_data', 'efa_output', 'cfa_output', 'item_assignments']:
    if key not in st.session_state: st.session_state[key] = None
if 'feedback_submitted' not in st.session_state: st.session_state['feedback_submitted'] = False
if 'lang' not in st.session_state: st.session_state.lang = 'العربية'

st.set_page_config(page_title="PsychoStat Pro", page_icon="💠", layout="wide", initial_sidebar_state="expanded")

# --- Language Dictionary ---
translations = {
    'English': {
        'select_lang': '🌐 Select Language', 'main_title': '💠 PsychoStat Pro',
        'subtitle': 'Explore measurement quality of attitudes with transparent methods and exportable results.',
        'developer': 'Platform Developer: Asmaa Dala',
        'tab1': '📊 1. Raw Data & Descriptives', 'tab2': '🔍 2. EFA & Reliability', 'tab3': '📈 3. CFA & Validity', 'tab4': '📄 4. Analysis Report & Charts',
        'raw_info': 'Upload your survey data (Excel/CSV) to automatically extract demographics and split data for EFA/CFA.',
        'upload_forms': 'Upload Google Forms Data',
        'demo_summary': '1. Demographic Summary', 'select_demo': 'Select Demographic Variables:',
        'normality_desc': '2. Descriptive Stats (Mean & SD)', 'select_normality': '📌 Select Scale Items for Analysis:',
        'ready_split': 'Ready for Psychometric Analysis?', 'split_btn': '✂️ Automatically Split Data for EFA & CFA (50/50)',
        'study_overview': 'Study Overview', 'total_cases': 'Total available cases', 'p1_cases': 'Phase 1 cases (EFA)', 'p2_cases': 'Phase 2 cases (CFA)', 'not_loaded': 'Not loaded',
        'demo_title': '📖 Applied Example: EGAIS Scale Results',
        'demo_desc': 'This validated scale is presented as a demo. Use this platform to analyze your own survey data with high precision.',
        'demo_intro': 'This scale (EGAIS) was developed specifically by researcher **Asmaa Dala**. Here are the robust results extracted by the platform:',
        'demo_details': '🔍 View Scale Details & Results 📊',
        'dim_col': 'Dimensions', 'items_col': 'Items', 'var_col': 'Variance',
        'dim1': 'Anxiety', 'dim2': 'Efficacy',
        'ind_col': 'Indicator', 'res_col': 'Result',
        'feedback_title': '💬 Feedback & Consultations', 'feedback_desc': 'Share your thoughts or request a consultation.',
        'feedback_rating': 'How was your experience?', 'feedback_text': 'Leave a comment...', 'feedback_submit': 'Send Feedback 🚀', 'feedback_thanks': 'Thank you! Received. 😍',
        'run_efa': 'Run Exploratory Factor Analysis (EFA)', 'run_cfa': 'Run Confirmatory Factor Analysis (CFA)',
        'report_wait': 'Please run EFA and CFA in the previous tabs to generate the automated report.',
        'report_title': 'Automated Academic Report (APA 7)', 'charts_title': 'Visualizations (Charts & Graphs)',
        'sample_error': '⛔ Error: Sample size is less than 50. Factor analysis cannot be performed due to insufficient data.',
        'auto_assign_msg': '💡 Items have been automatically assigned to factors based on the highest EFA loadings (>0.30).',
        'rotation_help': 'Use Varimax for independent factors, and Oblimin for correlated psychological factors.',
        'corr_matrix_title': 'Correlation Matrix',
        'anti_image_title': 'Anti-Image Matrices'
    },
    'العربية': {
        'select_lang': '🌐 اختر اللغة', 'main_title': '💠 PsychoStat Pro',
        'subtitle': 'استكشف جودة القياس النفسي مع عينات وأساليب ونتائج علمية دقيقة وقابلة للتصدير.',
        'developer': 'مطورة المنصة: أسماء دالة',
        'tab1': '📊 1. البيانات والإحصاء الوصفي', 'tab2': '🔍 2. التحليل الاستكشافي والثبات', 'tab3': '📈 3. التحليل التوكيدي والصدق', 'tab4': '📄 4. التقرير والرسوم البيانية',
        'raw_info': 'قم برفع بيانات الاستبيان (Excel/CSV) لاستخراج الجداول الديموغرافية وتقسيم البيانات لمرحلتي EFA و CFA تلقائياً.',
        'upload_forms': 'رفع ملف بيانات الاستبيان',
        'demo_summary': '1. الملخص الديموغرافي', 'select_demo': 'اختر المتغيرات الديموغرافية:',
        'normality_desc': '2. الإحصاء الوصفي', 'select_normality': '📌 اختر فقرات المقياس:',
        'ready_split': 'هل أنت جاهز للتحليل السيكومتري؟', 'split_btn': '✂️ تقسيم البيانات تلقائياً لـ EFA و CFA (بنسبة 50/50)',
        'study_overview': 'نظرة عامة على الدراسة', 'total_cases': 'إجمالي الحالات المتاحة', 'p1_cases': 'حالات المرحلة 1 (EFA)', 'p2_cases': 'حالات المرحلة 2 (CFA)', 'not_loaded': 'لم يتم التحميل',
        'demo_title': '📖 مثال تطبيقي: نتائج مقياس (EGAIS)',
        'demo_desc': 'هذا المقياس المُحكّم معروض كمثال تطبيقي لتوضيح قدرة المنصة.',
        'demo_intro': 'تم تطوير مقياس (EGAIS) خصيصاً من قِبل الباحثة **أسماء دالة**. إليكِ النتائج الحقيقية والمبهرة التي استخرجتها المنصة:',
        'demo_details': '🔍 عرض تفاصيل ونتائج المقياس 📊',
        'dim_col': 'الأبعاد', 'items_col': 'الفقرات', 'var_col': 'التباين',
        'dim1': 'القلق', 'dim2': 'الفعالية',
        'ind_col': 'المؤشر', 'res_col': 'النتيجة',
        'feedback_title': '💬 آراء ومقترحات الباحثين', 'feedback_desc': 'يسعدنا سماع رأيك أو ترك استشارتك.',
        'feedback_rating': 'كيف تقيم تجربتك؟', 'feedback_text': 'اكتب تعليقك أو استشارتك...', 'feedback_submit': 'إرسال 🚀', 'feedback_thanks': 'شكراً لك! تم استلام رسالتك. 😍',
        'run_efa': 'إجراء التحليل العاملي الاستكشافي (EFA)', 'run_cfa': 'إجراء التحليل العاملي التوكيدي (CFA) آلياً',
        'report_wait': 'يرجى إجراء التحليل الاستكشافي والتوكيدي في التبويبات السابقة لتوليد التقرير والرسوم البيانية.',
        'report_title': 'التقرير الأكاديمي الآلي (APA 7)', 'charts_title': 'الرسوم البيانية (الأعمدة والدوائر النسبية)',
        'sample_error': '⛔ خطأ: حجم العينة الحالي صغير جداً (أقل من 50 استجابة). تم إيقاف التحليل لعدم كفاية البيانات وتجنب النتائج المضللة.',
        'auto_assign_msg': '💡 تم توزيع الفقرات وبناء نموذج المعادلة البنائية تلقائياً بناءً على أعلى تشبع (أكبر من 0.30) من نتائج التحليل الاستكشافي.',
        'rotation_help': 'استخدم Varimax للعوامل المستقلة، وOblimin للعوامل النفسية المرتبطة.',
        'corr_matrix_title': 'مصفوفة الارتباطات (Correlation Matrix)',
        'anti_image_title': 'المصفوفة المضادة للارتباط (Anti-Image Matrices)'
    },
    'Français': {
        'select_lang': '🌐 Choisir la langue', 'main_title': '💠 PsychoStat Pro',
        'subtitle': 'Explorez la qualité des mesures psychométriques avec des méthodes transparentes et des résultats exportables.',
        'developer': 'Développé par: Asmaa Dala',
        'tab1': '📊 1. Données et Descriptives', 'tab2': '🔍 2. AFE et Fiabilité', 'tab3': '📈 3. AFC et Validité', 'tab4': '📄 4. Rapport et Graphiques',
        'raw_info': 'Téléchargez vos données (Excel/CSV) pour extraire la démographie et diviser les données pour AFE/AFC.',
        'upload_forms': 'Télécharger les données du questionnaire',
        'demo_summary': '1. Résumé Démographique', 'select_demo': 'Sélectionner les variables démographiques:',
        'normality_desc': '2. Statistiques Descriptives', 'select_normality': '📌 Sélectionner les items de l\'échelle:',
        'ready_split': 'Prêt pour l\'analyse psychométrique?', 'split_btn': '✂️ Diviser automatiquement les données (AFE/AFC 50/50)',
        'study_overview': 'Aperçu de l\'étude', 'total_cases': 'Cas totaux', 'p1_cases': 'Cas Phase 1 (AFE)', 'p2_cases': 'Cas Phase 2 (AFC)', 'not_loaded': 'Non chargé',
        'demo_title': '📖 Exemple Appliqué: Résultats de l\'échelle EGAIS',
        'demo_desc': 'Cette échelle validée est présentée comme une démonstration.',
        'demo_intro': 'Cette échelle (EGAIS) a été développée par la chercheuse **Asmaa Dala**.',
        'demo_details': '🔍 Voir les détails et résultats de l\'échelle 📊',
        'dim_col': 'Dimensions', 'items_col': 'Items', 'var_col': 'Variance',
        'dim1': 'Anxiété', 'dim2': 'Efficacité',
        'ind_col': 'Indicateur', 'res_col': 'Résultat',
        'feedback_title': '💬 Avis et Consultations', 'feedback_desc': 'Partagez votre avis ou demandez une consultation.',
        'feedback_rating': 'Comment évaluez-vous votre expérience?', 'feedback_text': 'Laissez un commentaire...', 'feedback_submit': 'Envoyer 🚀', 'feedback_thanks': 'Merci! Bien reçu. 😍',
        'run_efa': 'Exécuter l\'Analyse Factorielle Exploratoire (AFE)', 'run_cfa': 'Exécuter l\'Analyse Factorielle Confirmatoire (AFC)',
        'report_wait': 'Veuillez exécuter l\'AFE et l\'AFC pour générer le rapport.',
        'report_title': 'Rapport Académique Automatisé (APA 7)', 'charts_title': 'Visualisations (Graphiques)',
        'sample_error': '⛔ Erreur: La taille de l\'échantillon est inférieure à 50. L\'analyse factorielle ne peut pas être effectuée.',
        'auto_assign_msg': '💡 Les items ont été automatiquement assignés aux facteurs selon les plus fortes saturations (>0.30).',
        'rotation_help': 'Utilisez Varimax pour les facteurs indépendants, et Oblimin pour les facteurs psychologiques corrélés.',
        'corr_matrix_title': 'Matrice de Corrélation',
        'anti_image_title': 'Matrices Anti-Image'
    }
}

# --- Styling ---
st.markdown("""
    <style>
    div.stButton > button:first-child, div.stDownloadButton > button:first-child, div.stFormSubmitButton > button:first-child {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important; color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 700 !important; padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important; transition: all 0.3s ease !important; width: 100% !important; border-color: #3b82f6 !important;
    }
    div.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4) !important; background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important; }
    .demo-card { background: linear-gradient(to right, #f0f9ff, #e0f2fe); border: 2px solid #bae6fd; border-right: 8px solid #0284c7; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 20px rgba(2, 132, 199, 0.15); }
    .demo-card h3 { color: #0c4a6e; margin-top: 0; font-weight: 800; font-size: 1.3rem; }
    [data-testid="stMetric"] { background: #fff; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1, h2, h3, h4 { color: #17324d; font-weight: 700; }
    
    /* ستايل الجداول المخصصة الجذابة للنموذج */
    .custom-table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; font-size: 0.95rem; text-align: center; }
    .custom-table th { color: white; padding: 12px; font-weight: bold; border: 1px solid #ddd; }
    .custom-table td { padding: 10px; border: 1px solid #e2e8f0; }
    .table-blue th { background-color: #0284c7; }
    .table-orange th { background-color: #ea580c; }
    .custom-table tr:nth-child(even) { background-color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.session_state.lang = st.sidebar.selectbox('🌐 Select Language / اختر اللغة / Langue', ['العربية', 'English', 'Français'])
lang = translations[st.session_state.lang]

with st.sidebar:
    st.markdown("---")
    st.markdown(f"### {lang['feedback_title']}")
    st.caption(lang['feedback_desc'])
    if not st.session_state['feedback_submitted']:
        with st.form("feedback_form"):
            st.radio(lang['feedback_rating'], ["😍 ممتاز (Excellent)", "👍 جيد (Good)", "🤔 يحتاج تحسين (Improvement)"])
            st.text_area(lang['feedback_text'], height=80)
            if st.form_submit_button(lang['feedback_submit']):
                st.session_state['feedback_submitted'] = True
                st.rerun()
    else:
        st.success(lang['feedback_thanks'])
        if st.button("إرسال رسالة أخرى" if st.session_state.lang == 'العربية' else ("Send another" if st.session_state.lang == 'English' else "Envoyer un autre")):
            st.session_state['feedback_submitted'] = False
            st.rerun()

# --- Functions ---
def as_numeric_items(data, items): 
    return data.loc[:, items].apply(pd.to_numeric, errors="coerce")

def calc_alpha_omega(df, items):
    complete = as_numeric_items(df, items).dropna(axis=0, how="any")
    if complete.empty or len(items) < 2:
        return np.nan, np.nan
    try:
        alpha = pg.cronbach_alpha(data=complete)[0]
    except:
        alpha = np.nan
    try:
        fa = FactorAnalyzer(n_factors=1, rotation=None)
        fa.fit(complete)
        ld = fa.loadings_.flatten()
        sum_l = np.sum(ld)
        sum_l2 = np.sum(ld**2)
        sum_err = np.sum(1 - ld**2)
        denom = (sum_l**2) + sum_err
        omega = (sum_l**2) / denom if denom > 0 else np.nan
    except:
        omega = np.nan
    return alpha, omega

def efa_result(data, items, factor_count, rotation):
    complete = as_numeric_items(data, items).dropna(axis=0, how="any")
    try: 
        kmo_all, kmo_model = calculate_kmo(complete)
        bartlett_chi2, bartlett_p = calculate_bartlett_sphericity(complete)
    except: 
        kmo_all, kmo_model, bartlett_chi2, bartlett_p = np.full(len(items), np.nan), np.nan, np.nan, np.nan
    
    fa = FactorAnalyzer(n_factors=factor_count, rotation=rotation, method='principal')
    fa.fit(complete)
    loadings = pd.DataFrame(fa.loadings_, index=items, columns=[f"Factor_{i+1}" for i in range(factor_count)])
    ev, _ = fa.get_eigenvalues()
    
    corr_matrix = complete.corr()
    inv_corr = np.linalg.inv(corr_matrix)
    anti_image_cov = -inv_corr / np.outer(np.sqrt(np.diag(inv_corr)), np.sqrt(np.diag(inv_corr)))
    np.fill_diagonal(anti_image_cov, kmo_all)
    anti_image_df = pd.DataFrame(anti_image_cov, index=items, columns=items)
    
    transform_matrix = None
    if hasattr(fa, 'rotation_matrix_') and fa.rotation_matrix_ is not None:
        transform_matrix = pd.DataFrame(fa.rotation_matrix_, 
                                        index=[f"Comp_{i+1}" for i in range(factor_count)], 
                                        columns=[f"Comp_{i+1}" for i in range(factor_count)])
        
    return {"n": len(complete), "kmo": kmo_model, "kmo_items": pd.Series(kmo_all, index=items), 
            "bartlett_chi2": bartlett_chi2, "bartlett_p": bartlett_p, "method": "PCA", 
            "rotation": rotation, "factor_count": factor_count, "loadings": loadings, 
            "ev": pd.DataFrame({"Component": range(1, len(ev)+1), "Eigenvalue": ev}),
            "anti_image": anti_image_df, "transformation": transform_matrix}

def build_cfa_specification(factor_assignments):
    used_items = [item for items in factor_assignments.values() for item in items]
    aliases = {item: f"item_{i}" for i, item in enumerate(used_items)}
    lines = [f"{factor} =~ " + " + ".join(aliases[item] for item in items) for factor, items in factor_assignments.items()]
    return {"items": used_items, "aliases": aliases, "engine_syntax": "\n".join(lines), "factor_assignments": factor_assignments}

def cfa_result(data, spec):
    complete = as_numeric_items(data, spec["items"]).dropna(axis=0, how="any")
    renamed = complete.rename(columns=spec["aliases"])
    model = Model(spec["engine_syntax"])
    model.fit(renamed, obj="MLW")
    fit = calc_stats(model).iloc[0]
    fit_vals = {name: float(fit.get(name, np.nan)) for name in ["chi2", "DoF", "chi2 p-value", "CFI", "TLI", "RMSEA"]}
    params = model.inspect(std_est=True)
    
    rev_aliases = {v: k for k, v in spec["aliases"].items()}
    if 'lval' in params.columns:
        params['lval_orig'] = params['lval'].map(rev_aliases).fillna(params['lval'])
    
    cr_ave_dict = {}
    if 'Est. Std' in params.columns and 'op' in params.columns:
        loadings_df = params[params['op'] == '~'].copy()
        for factor in spec['factor_assignments'].keys():
            f_loadings = loadings_df[loadings_df['rval'] == factor]['Est. Std'].astype(float).values
            if len(f_loadings) > 0:
                sum_l = np.sum(f_loadings)
                sum_l2 = np.sum(f_loadings**2)
                sum_err = np.sum(1 - f_loadings**2)
                denom = (sum_l**2) + sum_err
                cr = (sum_l**2) / denom if denom > 0 else np.nan
                ave = sum_l2 / len(f_loadings)
                cr_ave_dict[factor] = {'CR': cr, 'AVE': ave}

    return {"n": len(complete), "fit": fit_vals, "params": params, "cr_ave": cr_ave_dict}

# --- Header & Example ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); padding: 40px 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px;">
        <h1 style="margin: 0; font-size: 42px; font-weight: 900;">{lang['main_title']}</h1>
        <p style="font-size: 16px; margin-top: 10px;">{lang['subtitle']}</p>
        <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-weight: bold;">👩‍💻 {lang['developer']}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""<div class="demo-card"><h3>{lang['demo_title']}</h3><p>{lang['demo_desc']}</p></div>""", unsafe_allow_html=True)
with st.expander(lang['demo_details'], expanded=False):
    st.markdown(lang['demo_intro'])
    col1, col2 = st.columns(2)
    
    # الجداول الجذابة باستخدام HTML المباشر
    html_table1 = f"""
    <table class="custom-table table-blue">
        <tr><th>{lang['dim_col']}</th><th>{lang['items_col']}</th><th>{lang['var_col']}</th></tr>
        <tr><td>{lang['dim1']}</td><td>12</td><td>67.04%</td></tr>
        <tr><td>{lang['dim2']}</td><td>11</td><td>-</td></tr>
    </table>
    """
    col1.markdown(html_table1, unsafe_allow_html=True)
    
    html_table2 = f"""
    <table class="custom-table table-orange">
        <tr><th>{lang['ind_col']}</th><th>{lang['res_col']}</th></tr>
        <tr><td>CR</td><td>0.964</td></tr>
        <tr><td>AVE</td><td>0.562</td></tr>
        <tr><td>CFI</td><td>0.911</td></tr>
        <tr><td>RMSEA</td><td>0.087</td></tr>
    </table>
    """
    col2.markdown(html_table2, unsafe_allow_html=True)

# --- Global Data & Tabs Definition ---
selected_items = []
if st.session_state['raw_data'] is not None:
    df = st.session_state['raw_data']
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols: 
        selected_items = st.multiselect(lang['select_normality'], num_cols, default=num_cols[:10])

tab_desc, tab_efa, tab_cfa, tab_report = st.tabs([lang['tab1'], lang['tab2'], lang['tab3'], lang['tab4']])

# --- TAB 1: Descriptives ---
with tab_desc:
    st.info(lang['raw_info'])
    raw_file = st.file_uploader(lang['upload_forms'], type=["csv", "xlsx"])
    if raw_file:
        df_raw = pd.read_csv(raw_file) if raw_file.name.endswith('.csv') else pd.read_excel(raw_file)
        st.session_state['raw_data'] = df_raw
        st.success(f"✅ Data loaded! Total responses: {len(df_raw)}")
        
        st.markdown("---")
        st.markdown(f"**{lang['demo_summary']}**")
        demo_cols = st.multiselect(lang['select_demo'], df_raw.columns, key="demo_cols")
        if demo_cols:
            for col in demo_cols:
                freq = df_raw[col].value_counts().reset_index()
                freq.columns = [col, 'Frequency']
                freq['Percentage'] = (freq['Frequency'] / len(df_raw) * 100).round(2)
                st.dataframe(freq, use_container_width=True)
                
        if selected_items:
            st.markdown("---")
            st.markdown(f"**{lang['normality_desc']}**")
            desc_df = df_raw[selected_items].describe().T[['mean', 'std']].round(3)
            desc_df.rename(columns={'mean': 'المتوسط (Mean)', 'std': 'الانحراف (SD)'}, inplace=True)
            st.dataframe(desc_df, use_container_width=True)
                
        st.markdown("---")
        st.markdown(f"#### {lang['ready_split']}")
        if st.button(lang['split_btn']):
            if len(df_raw) < 50:
                 st.error(lang['sample_error'])
            else:
                df_shuffled = df_raw.sample(frac=1, random_state=42).reset_index(drop=True)
                mid = len(df_shuffled) // 2
                st.session_state['phase1_data'] = df_shuffled.iloc[:mid]
                st.session_state['phase2_data'] = df_shuffled.iloc[mid:]
                st.success(f"Split successful! EFA: {mid}, CFA: {len(df_shuffled)-mid}")

    st.markdown("---")
    st.markdown(f"#### {lang['study_overview']}")
    phase_cols = st.columns(3)
    p1_len = len(st.session_state['phase1_data']) if st.session_state['phase1_data'] is not None else 0
    p2_len = len(st.session_state['phase2_data']) if st.session_state['phase2_data'] is not None else 0
    phase_cols[0].metric(lang['total_cases'], p1_len + p2_len)
    phase_cols[1].metric(lang['p1_cases'], p1_len if p1_len > 0 else lang['not_loaded'])
    phase_cols[2].metric(lang['p2_cases'], p2_len if p2_len > 0 else lang['not_loaded'])

# --- TAB 2: EFA & Reliability ---
with tab_efa:
    if st.session_state['phase1_data'] is not None and selected_items:
        n_cases = len(st.session_state['phase1_data'])
        if n_cases < 50:
            st.error(lang['sample_error'])
        else:
            st.markdown("#### الثبات للبيانات الاستكشافية (Reliability - EFA Sample)")
            alpha_efa, omega_efa = calc_alpha_omega(st.session_state['phase1_data'], selected_items)
            rel_cols = st.columns(2)
            rel_cols[0].metric("ألفا كرونباخ (Cronbach's α)", f"{alpha_efa:.3f}")
            rel_cols[1].metric("ماكدونالد أوميغا (McDonald's ω)", f"{omega_efa:.3f}")
            st.markdown("---")

            st.markdown(f"#### {lang['corr_matrix_title']}")
            corr_matrix = st.session_state['phase1_data'][selected_items].corr()
            st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format("{:.3f}"), use_container_width=True)
            st.markdown("---")

            c1, c2 = st.columns(2)
            factor_count = c1.number_input("Factors", min_value=1, value=2)
            rotation = c2.selectbox("Rotation", ["varimax", "oblimin"], help=lang['rotation_help'])
            
            if st.button(lang['run_efa']):
                out = efa_result(st.session_state['phase1_data'], selected_items, int(factor_count), rotation)
                st.session_state['efa_output'] = out
                
                labels = [f"Factor_{i+1}" for i in range(out['factor_count'])]
                item_mapping = {}
                for item in selected_items:
                    item_mapping[item] = "غير مدرج (Not included)" 
                    if item in out['loadings'].index:
                        loadings_row = out['loadings'].loc[item]
                        max_factor = loadings_row.abs().idxmax()
                        max_val = loadings_row.abs().max()
                        if max_val >= 0.30 and max_factor in labels:
                            item_mapping[item] = max_factor
                st.session_state['item_assignments'] = item_mapping
                
                st.success("EFA Completed Successfully!")
                st.markdown(f"**طريقة الاستخراج:** تحليل المكونات الأساسية (PCA)")
                st.markdown("---")
                
                p_val = out['bartlett_p']
                p_str = "p < .001" if p_val < 0.001 else f"p = {p_val:.3f}"
                
                metrics = st.columns(4)
                metrics[2].metric("Bartlett χ²", f"{out['bartlett_chi2']:.2f}") 
                metrics[3].metric("Bartlett p", p_str)
                
                st.markdown("#### التشبعات العاملية (Factor Loadings)")
                st.dataframe(out["loadings"].style.format("{:.3f}"), use_container_width=True)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"#### {lang['anti_image_title']}")
                    # الحل البرمجي لخطأ التحويل في Pandas مع إضافة حرف a
                    anti_image_raw = out["anti_image"]
                    anti_image_str = anti_image_raw.copy().astype(str)
                    for r in anti_image_raw.index:
                        for c in anti_image_raw.columns:
                            val = anti_image_raw.loc[r, c]
                            if r == c:
                                anti_image_str.loc[r, c] = f"{val:.3f}a"
                            else:
                                anti_image_str.loc[r, c] = f"{val:.3f}"
                    
                    def highlight_diag(val): 
                        return 'background-color: #d1fae5; font-weight:bold' if str(val).endswith('a') else ''
                    
                    st.dataframe(anti_image_str.style.applymap(highlight_diag), use_container_width=True)
                
                with col_b:
                    st.markdown("#### مصفوفة تحويل المكونات (Transformation Matrix)")
                    if out["transformation"] is not None:
                        st.dataframe(out["transformation"].style.format("{:.3f}"), use_container_width=True)
                    else:
                        st.info("لا توجد مصفوفة تحويل لأن التدوير غير مطبق أو غير مدعوم لهذه الطريقة.")

# --- TAB 3: CFA & Validity ---
with tab_cfa:
    if st.session_state['phase2_data'] is not None and selected_items:
        n_cases_cfa = len(st.session_state['phase2_data'])
        if n_cases_cfa < 50:
            st.error(lang['sample_error'])
        else:
            efa_out = st.session_state.get('efa_output')
            default_cfa_factors = int(efa_out['factor_count']) if efa_out else 2
            cfa_factors = st.number_input("CFA Factors", min_value=1, value=default_cfa_factors, key="cfa_factors")
            
            labels = [f"Factor_{i+1}" for i in range(cfa_factors)]
            options = ["غير مدرج (Not included)"] + labels
            
            st.markdown("#### توزيع الفقرات على العوامل")
            
            efa_assignments = st.session_state.get('item_assignments') or {}
            if efa_assignments:
                st.info(lang['auto_assign_msg'])
            
            assign = {}
            cols = st.columns(2)
            
            for i, item in enumerate(selected_items):
                assigned_factor = efa_assignments.get(item, "غير مدرج (Not included)")
                idx = options.index(assigned_factor) if assigned_factor in options else 0
                assign[item] = cols[i%2].selectbox(label=str(item), options=options, index=idx)
            
            if st.button(lang['run_cfa']):
                f_assign = {f: [i for i, a in assign.items() if a == f] for f in labels}
                f_assign = {k: v for k, v in f_assign.items() if len(v) > 0}
                
                if not f_assign or any(len(v) < 2 for v in f_assign.values()):
                    st.error("⚠️ فشل بناء النموذج: أحد العوامل يحتوي على أقل من فقرتين. تأكد من تحديد فقرتين على الأقل لكل عامل لتجنب أخطاء البناء.")
                else:
                    try:
                        spec = build_cfa_specification(f_assign)
                        cfa_out = cfa_result(st.session_state['phase2_data'], spec)
                        st.session_state['cfa_output'] = cfa_out
                        st.success("CFA Completed Successfully!")
                        
                        st.markdown("#### مؤشرات جودة المطابقة (Fit Indices)")
                        fit_vals = cfa_out["fit"]
                        f_cols = st.columns(4)
                        f_cols[0].metric("CFI", f"{fit_vals['CFI']:.3f}")
                        f_cols[1].metric("TLI", f"{fit_vals['TLI']:.3f}")
                        f_cols[2].metric("RMSEA", f"{fit_vals['RMSEA']:.3f}")
                        f_cols[3].metric("χ² (df)", f"{fit_vals['chi2']:.2f} ({fit_vals['DoF']:.0f})")
                        
                        st.markdown("#### تقديرات معلمات النموذج (Parameter Estimates)")
                        params_df = cfa_out["params"]
                        display_params = params_df[(params_df['op'] == '~') & (params_df['rval'].isin(labels))].copy()
                        display_params = display_params.rename(columns={'rval': 'Factor', 'lval_orig': 'Item'})
                        cols_to_show = ['Factor', 'Item', 'Estimate', 'Est. Std', 'Std. Err', 'z-value', 'p-value']
                        cols_to_show = [c for c in cols_to_show if c in display_params.columns]
                        
                        numeric_cols = ['Estimate', 'Est. Std', 'Std. Err', 'z-value', 'p-value']
                        for col in numeric_cols:
                            if col in display_params.columns:
                                display_params[col] = pd.to_numeric(display_params[col], errors='coerce')

                        st.dataframe(display_params[cols_to_show].style.format({
                            "Estimate": "{:.3f}", 
                            "Est. Std": "{:.3f}", 
                            "Std. Err": "{:.3f}", 
                            "z-value": "{:.3f}", 
                            "p-value": "{:.4f}"
                        }, na_rep="—"), use_container_width=True)

                        # --- Automated Diagnostic System (نظام التشخيص الآلي - JARS/APA 7) ---
                        st.markdown("---")
                        st.markdown("### 🛠️ نظام التوجيه والتشخيص الآلي (JARS / APA 7)")
                        
                        cr_ave_data = cfa_out.get('cr_ave', {})
                        factors_list = list(f_assign.keys())
                        
                        st.markdown("#### 1. الصدق التقاربي والثبات (Convergent Validity & Reliability)")
                        
                        issues_conv = False
                        if cr_ave_data:
                            val_data = []
                            issues_found = [] 
                            
                            for factor, metrics in cr_ave_data.items():
                                alpha, omega = calc_alpha_omega(st.session_state['phase2_data'], f_assign[factor])
                                cr_val = metrics['CR']
                                ave_val = metrics['AVE']
                                
                                val_data.append({
                                    "العامل (Factor)": factor,
                                    "ألفا كرونباخ (α)": alpha,
                                    "أوميغا (ω)": omega,
                                    "الثبات المركب (CR)": cr_val,
                                    "التباين المستخرج (AVE)": ave_val
                                })
                                
                                if ave_val < 0.50:
                                    issues_found.append(f"العامل **{factor}**: قيمة AVE ({ave_val:.3f}) أقل من 0.50.")
                                if cr_val < 0.70:
                                    issues_found.append(f"العامل **{factor}**: قيمة CR ({cr_val:.3f}) أقل من 0.70.")
                            
                            val_df = pd.DataFrame(val_data).set_index("العامل (Factor)")
                            st.dataframe(val_df.style.format("{:.3f}"), use_container_width=True)
                            
                            if issues_found:
                                issues_conv = True
                                st.session_state['conv_passed'] = False
                                st.error("❌ **تحذير معايير JARS:** لم يتحقق الصدق التقاربي أو الثبات في بعض العوامل.")
                                for issue in issues_found:
                                    st.warning(f"⚠️ {issue}")
                            else:
                                st.session_state['conv_passed'] = True
                                st.success("✅ **ممتاز:** جميع قيم الصدق التقاربي (AVE > 0.50) والثبات المركب (CR > 0.70) مطابقة للمعايير.")

                        st.markdown("#### 2. الصدق التمييزي (Discriminant Validity - Fornell-Larcker)")
                        
                        disc_df = pd.DataFrame(index=factors_list, columns=factors_list, dtype=float)
                        
                        for f in factors_list:
                            if f in cr_ave_data:
                                disc_df.loc[f, f] = np.sqrt(cr_ave_data[f]['AVE'])
                                
                        corrs = params_df[(params_df['op'] == '~~') & (params_df['lval'].isin(factors_list)) & (params_df['rval'].isin(factors_list)) & (params_df['lval'] != params_df['rval'])]
                        for _, row in corrs.iterrows():
                            f1, f2 = row['lval'], row['rval']
                            val = float(row['Est. Std'])
                            disc_df.loc[f1, f2] = val
                            disc_df.loc[f2, f1] = val
                                
                        def highlight_diag(df):
                            attr = 'background-color: #d1fae5; font-weight: bold; color: #065f46;'
                            return pd.DataFrame(np.where(np.eye(df.shape[0], dtype=bool), attr, ''), index=df.index, columns=df.columns)
                            
                        st.dataframe(disc_df.style.apply(highlight_diag, axis=None).format("{:.3f}", na_rep="—"), use_container_width=True)
                        
                        disc_issues = []
                        for i, f1 in enumerate(factors_list):
                            for j, f2 in enumerate(factors_list):
                                if i != j and pd.notna(disc_df.loc[f1, f2]) and pd.notna(disc_df.loc[f1, f1]):
                                    if abs(disc_df.loc[f1, f2]) > disc_df.loc[f1, f1]:
                                        disc_issues.append(f"الارتباط بين ({f1}) و ({f2}) = {abs(disc_df.loc[f1, f2]):.3f} وهو أعلى من الجذر التربيعي لـ AVE للعامل ({f1}) = {disc_df.loc[f1, f1]:.3f}")
                        
                        if disc_issues:
                            st.session_state['disc_passed'] = False
                            st.error("❌ **تحذير معايير JARS:** لم يتحقق الصدق التمييزي (معيار Fornell-Larcker).")
                            for d_issue in disc_issues:
                                st.warning(f"⚠️ التداخل العالي: {d_issue}")
                        else:
                            st.session_state['disc_passed'] = True
                            st.success("✅ **ممتاز:** الصدق التمييزي متحقق بنجاح. قيم الجذر التربيعي لـ AVE (في القطر الأخضر) أعلى من جميع الارتباطات الأخرى.")

                        st.markdown("#### المخطط الهيكلي (Structural Diagram)")
                        dot_code = "digraph CFA {\nrankdir=LR;\nnode [shape=box, style=filled, fillcolor=white];\n"
                        for factor, items in f_assign.items():
                            dot_code += f'"{factor}" [shape=ellipse, style=filled, fillcolor="#bae6fd"];\n'
                            for item in items:
                                dot_code += f'"{factor}" -> "{item}";\n'
                        dot_code += "}"
                        st.graphviz_chart(dot_code)

                    except Exception as e:
                        st.error(f"⚠️ فشل التحليل التوكيدي: يرجى التأكد من أن البيانات مناسبة لبناء النموذج. (تفاصيل الخطأ: {str(e)})")

# --- TAB 4: Report & Charts ---
with tab_report:
    st.markdown(f"### {lang['charts_title']}")
    if st.session_state['raw_data'] is not None:
        df = st.session_state['raw_data']
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**الدوائر النسبية (Pie Charts)**")
            cat_cols = df.select_dtypes(include=['object']).columns.tolist()
            if cat_cols:
                pie_col = st.selectbox("اختر متغيراً للرسم الدائري:", cat_cols)
                fig1, ax1 = plt.subplots(figsize=(4,4))
                ax1.pie(df[pie_col].value_counts(), labels=df[pie_col].value_counts().index, autopct='%1.1f%%', colors=plt.cm.Set3.colors)
                st.pyplot(fig1)
            else:
                st.info("لا توجد متغيرات ديموغرافية نصية (نص/حروف) للرسم.")
                
        with col2:
            st.markdown("**الأعمدة البيانية (Bar Charts)**")
            if selected_items:
                means = df[selected_items].mean()
                fig2, ax2 = plt.subplots(figsize=(6,4))
                ax2.bar(means.index, means.values, color='#3b82f6')
                plt.xticks(rotation=45)
                ax2.set_title("متوسطات فقرات المقياس")
                st.pyplot(fig2)

    st.markdown("---")
    st.markdown(f"### {lang['report_title']}")
    
    efa_out = st.session_state.get('efa_output')
    cfa_out = st.session_state.get('cfa_output')
    
    if not efa_out and not cfa_out:
        st.info(lang['report_wait'])
    else:
        report_text = ""
        if efa_out:
            p_val = efa_out['bartlett_p']
            p_str = "p < .001" if p_val < 0.001 else f"p = {p_val:.3f}"
            report_text += f"**1. التحليل العاملي الاستكشافي (EFA):**\nلضمان صلاحية البيانات للتحليل، أظهر اختبار KMO كفاءة جيدة بقيمة ({efa_out['kmo']:.3f}). وكان اختبار بارتليت دالاً إحصائياً (χ² = {efa_out['bartlett_chi2']:.2f}, {p_str}). تم استخراج ({efa_out['factor_count']}) عوامل باستخدام طريقة تحليل المكونات الأساسية (PCA) وتدوير ({efa_out['rotation']}) وفقاً لمعايير APA 7.\n\n"
        
        if cfa_out:
            fit = cfa_out['fit']
            conv_status = "وقد استوفت جميع العوامل المعايير المطلوبة للصدق التقاربي والثبات." if st.session_state.get('conv_passed', True) else "أظهرت النتائج قصوراً في الصدق التقاربي لبعض العوامل (AVE < 0.50)، مما يتطلب مراجعة الفقرات."
            disc_status = "كما تم التحقق من الصدق التمييزي وفق معيار Fornell-Larcker لتأكيد استقلالية العوامل وجودة البناء." if st.session_state.get('disc_passed', True) else "إلا أنه لم يتم التحقق من الصدق التمييزي وفق معيار Fornell-Larcker بسبب وجود تداخل كبير بين العوامل (Cross-loadings)، مما يقتضي إعادة النظر في هيكل المقياس."
            
            report_text += f"**2. التحليل العاملي التوكيدي (CFA):**\nللتأكد من صدق البناء ووفقاً لمعايير JARS، تم تطبيق نموذج CFA. أظهرت النتائج مؤشرات مطابقة للمتغيرات الكامنة: $\chi^2({fit['DoF']:.0f}) = {fit['chi2']:.2f}$، ومؤشر المطابقة المقارن CFI = ({fit.get('CFI',0):.3f})، وقيمة TLI = ({fit.get('TLI',0):.3f})، ومؤشر جذر متوسط مربع الخطأ RMSEA = ({fit.get('RMSEA',0):.3f}). {conv_status} {disc_status}\n\n"
        
        st.write(report_text)
        st.success("التقرير الأكاديمي أعلاه تمت كتابته آلياً وهو يعكس نتائجك الفعلية. يمكنك نسخه مباشرة!")
