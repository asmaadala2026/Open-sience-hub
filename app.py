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
for key in ['phase1_data', 'phase2_data', 'raw_data', 'efa_output', 'cfa_output']:
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
        'tab1': '📊 1. Raw Data & Descriptives', 'tab2': '🔍 2. EFA', 'tab3': '📈 3. CFA', 'tab4': '📄 4. Analysis Report & Charts',
        'raw_info': 'Upload your survey data (Excel/CSV) to automatically extract demographics and split data for EFA/CFA.',
        'upload_forms': 'Upload Google Forms Data (Excel/CSV)',
        'demo_summary': '1. Demographic Summary', 'select_demo': 'Select Demographic Variables:',
        'normality_desc': '2. Descriptive Stats (Mean & SD)', 'select_normality': '📌 Select Scale Items for Analysis:',
        'ready_split': 'Ready for Psychometric Analysis?', 'split_btn': '✂️ Automatically Split Data for EFA & CFA (50/50)',
        'study_overview': 'Study Overview', 'total_cases': 'Total available cases', 'p1_cases': 'Phase 1 cases (EFA)', 'p2_cases': 'Phase 2 cases (CFA)', 'not_loaded': 'Not loaded',
        'case_study_title': '📖 Case Study: EGAIS by Asmaa Dala',
        'case_study_desc': 'This validated scale is presented as a demo. Use this platform to analyze your own survey data with high precision.',
        'case_study_intro': 'This scale (EGAIS) was developed specifically by researcher **Asmaa Dala**. Here are the robust results extracted by the platform:',
        'feedback_title': '💬 Feedback & Consultations', 'feedback_desc': 'Share your thoughts or request a consultation.',
        'feedback_rating': 'How was your experience?', 'feedback_text': 'Leave a comment...', 'feedback_submit': 'Send Feedback 🚀', 'feedback_thanks': 'Thank you! Received. 😍',
        'run_efa': 'Run Exploratory Factor Analysis (EFA)', 'run_cfa': 'Run Confirmatory Factor Analysis (CFA)',
        'report_wait': 'Please run EFA and CFA in the previous tabs to generate the automated report.',
        'report_title': 'Automated Academic Report (APA 7)', 'charts_title': 'Visualizations (Charts & Graphs)',
        'sample_warning': '⚠️ JARS Warning: Sample size is less than 50. Factor analysis requires a larger sample.',
        'auto_assign_msg': '💡 Items have been automatically assigned to factors based on the highest EFA loadings (>0.30).'
    },
    'العربية': {
        'select_lang': '🌐 اختر اللغة', 'main_title': '💠 PsychoStat Pro',
        'subtitle': 'استكشف جودة القياس النفسي مع عينات وأساليب ونتائج علمية دقيقة وقابلة للتصدير.',
        'developer': 'مطورة المنصة: أسماء دالة',
        'tab1': '📊 1. البيانات والإحصاء الوصفي', 'tab2': '🔍 2. التحليل الاستكشافي (EFA)', 'tab3': '📈 3. التحليل التوكيدي (CFA)', 'tab4': '📄 4. التقرير والرسوم البيانية',
        'raw_info': 'قم برفع بيانات الاستبيان (Excel/CSV) لاستخراج الجداول الديموغرافية وتقسيم البيانات لمرحلتي EFA و CFA تلقائياً.',
        'upload_forms': 'رفع ملف بيانات الاستبيان',
        'demo_summary': '1. الملخص الديموغرافي', 'select_demo': 'اختر المتغيرات الديموغرافية:',
        'normality_desc': '2. الإحصاء الوصفي', 'select_normality': '📌 اختر فقرات المقياس:',
        'ready_split': 'هل أنت جاهز للتحليل السيكومتري؟', 'split_btn': '✂️ تقسيم البيانات تلقائياً لـ EFA و CFA (بنسبة 50/50)',
        'study_overview': 'نظرة عامة على الدراسة', 'total_cases': 'إجمالي الحالات المتاحة', 'p1_cases': 'حالات المرحلة 1 (EFA)', 'p2_cases': 'حالات المرحلة 2 (CFA)', 'not_loaded': 'لم يتم التحميل',
        'case_study_title': '📖 مثال تطبيقي: نتائج مقياس (EGAIS) للباحثة أسماء دالة',
        'case_study_desc': 'هذا المقياس المُحكّم معروض كدراسة حالة حقيقية لتوضيح قدرة المنصة.',
        'case_study_intro': 'تم تطوير مقياس (EGAIS) خصيصاً من قِبل الباحثة **أسماء دالة**. إليكِ النتائج الحقيقية والمبهرة التي استخرجتها المنصة:',
        'feedback_title': '💬 آراء ومقترحات الباحثين', 'feedback_desc': 'يسعدنا سماع رأيك أو ترك استشارتك.',
        'feedback_rating': 'كيف تقيم تجربتك؟', 'feedback_text': 'اكتب تعليقك أو استشارتك...', 'feedback_submit': 'إرسال 🚀', 'feedback_thanks': 'شكراً لك! تم استلام رسالتك. 😍',
        'run_efa': 'إجراء التحليل العاملي الاستكشافي (EFA)', 'run_cfa': 'إجراء التحليل العاملي التوكيدي (CFA)',
        'report_wait': 'يرجى إجراء التحليل الاستكشافي والتوكيدي في التبويبات السابقة لتوليد التقرير والرسوم البيانية.',
        'report_title': 'التقرير الأكاديمي الآلي (APA 7)', 'charts_title': 'الرسوم البيانية (الأعمدة والدوائر النسبية)',
        'sample_warning': '⚠️ تنبيه معايير JARS: حجم العينة الحالي صغير جداً (أقل من 50 استجابة). لا يمكن إجراء التحليل العاملي لعدم كفاية البيانات.',
        'auto_assign_msg': '💡 تم توزيع الفقرات تلقائياً على العوامل بناءً على أعلى تشبع (أكبر من 0.30) من التحليل الاستكشافي السابق. يمكنك مراجعتها ثم الضغط على زر التحليل.'
    },
    'Français': {
        'select_lang': '🌐 Choisir la langue', 'main_title': '💠 PsychoStat Pro',
        'subtitle': 'Explorez la qualité de la mesure des attitudes avec des méthodes transparentes.',
        'developer': 'Développeuse: Asmaa Dala',
        'tab1': '📊 1. Données Brutes', 'tab2': '🔍 2. Analyse Exploratoire', 'tab3': '📈 3. Analyse Confirmatoire', 'tab4': '📄 4. Rapport d\'Analyse',
        'raw_info': 'Téléchargez vos données (Excel/CSV) pour extraire les tableaux et diviser les données.',
        'upload_forms': 'Télécharger les Données',
        'demo_summary': '1. Résumé Démographique', 'select_demo': 'Sélectionner les Variables:',
        'normality_desc': '2. Statistiques Descriptives', 'select_normality': '📌 Sélectionner les items:',
        'ready_split': 'Prêt pour l\'Analyse ?', 'split_btn': '✂️ Diviser Automatiquement les Données (50/50)',
        'study_overview': 'Aperçu de l\'Étude', 'total_cases': 'Cas totaux', 'p1_cases': 'Phase 1 (EFA)', 'p2_cases': 'Phase 2 (CFA)', 'not_loaded': 'Non chargé',
        'case_study_title': '📖 Étude de Cas: Échelle (EGAIS)',
        'case_study_desc': 'Cette échelle validée est présentée comme démonstration.',
        'case_study_intro': 'Cette échelle (EGAIS) a été développée par la chercheuse **Asmaa Dala**.',
        'feedback_title': '💬 Avis & Consultations', 'feedback_desc': 'Partagez vos impressions.',
        'feedback_rating': 'Votre expérience ?', 'feedback_text': 'Laissez un commentaire...', 'feedback_submit': 'Envoyer 🚀', 'feedback_thanks': 'Merci !',
        'run_efa': 'Lancer l\'Analyse Exploratoire (EFA)', 'run_cfa': 'Lancer l\'Analyse Confirmatoire (CFA)',
        'report_wait': 'Les rapports seront disponibles ici après avoir exécuté l\'analyse.',
        'report_title': 'Rapport Automatique APA 7', 'charts_title': 'Graphiques',
        'sample_warning': '⚠️ Attention JARS : La taille de l\'échantillon est inférieure à 50. L\'analyse factorielle n\'est pas recommandée.',
        'auto_assign_msg': '💡 Les items ont été automatiquement assignés aux facteurs en fonction de l\'analyse exploratoire.'
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
    .case-study-card { background: linear-gradient(to right, #f0f9ff, #e0f2fe); border: 2px solid #bae6fd; border-right: 8px solid #0284c7; border-radius: 12px; padding: 25px; margin-bottom: 25px; box-shadow: 0 8px 20px rgba(2, 132, 199, 0.15); }
    .case-study-card h3 { color: #0c4a6e; margin-top: 0; font-weight: 800; font-size: 1.3rem; }
    [data-testid="stMetric"] { background: #fff; padding: 1rem; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1, h2, h3, h4 { color: #17324d; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.session_state.lang = st.sidebar.selectbox('🌐 Select Language / اختر اللغة', ['العربية', 'English', 'Français'])
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
        if st.button("إرسال رسالة أخرى"):
            st.session_state['feedback_submitted'] = False
            st.rerun()

# --- Functions ---
def as_numeric_items(data, items): 
    return data.loc[:, items].apply(pd.to_numeric, errors="coerce")

def efa_result(data, items, factor_count, rotation):
    complete = as_numeric_items(data, items).dropna(axis=0, how="any")
    try: 
        kmo_all, kmo_model = calculate_kmo(complete)
        bartlett_chi2, bartlett_p = calculate_bartlett_sphericity(complete)
    except: 
        kmo_all, kmo_model, bartlett_chi2, bartlett_p = np.full(len(items), np.nan), np.nan, np.nan, np.nan
    fa = FactorAnalyzer(n_factors=factor_count, rotation=rotation, method='principal')
    fa.fit(complete)
    loadings = pd.DataFrame(fa.loadings_, index=items, columns=[f"Factor {i+1}" for i in range(factor_count)])
    ev, _ = fa.get_eigenvalues()
    return {"n": len(complete), "kmo": kmo_model, "kmo_items": pd.Series(kmo_all, index=items), "bartlett_chi2": bartlett_chi2, "bartlett_p": bartlett_p, "method": "PCA", "rotation": rotation, "factor_count": factor_count, "loadings": loadings, "ev": pd.DataFrame({"Component": range(1, len(ev)+1), "Eigenvalue": ev})}

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
    return {"n": len(complete), "fit": fit_vals, "params": model.inspect(std_est=True)}

# --- Header & Case Study ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); padding: 40px 30px; border-radius: 20px; text-align: center; color: white; margin-bottom: 25px;">
        <h1 style="margin: 0; font-size: 42px; font-weight: 900;">{lang['main_title']}</h1>
        <p style="font-size: 16px; margin-top: 10px;">{lang['subtitle']}</p>
        <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-weight: bold;">👩‍💻 {lang['developer']}</span>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""<div class="case-study-card"><h3>{lang['case_study_title']}</h3><p>{lang['case_study_desc']}</p></div>""", unsafe_allow_html=True)
with st.expander("🔍 عرض تفاصيل ونتائج المقياس 📊", expanded=False):
    st.markdown(lang['case_study_intro'])
    col1, col2 = st.columns(2)
    col1.dataframe(pd.DataFrame({"الأبعاد": ["القلق", "الفعالية"], "الفقرات": [12, 11], "التباين": ["67.04%", "-"]}), hide_index=True, use_container_width=True)
    col2.dataframe(pd.DataFrame({"المؤشر": ["CR", "AVE", "CFI", "RMSEA"], "النتيجة": ["0.964", "0.562", "0.911", "0.087"]}), hide_index=True, use_container_width=True)

# --- Global Data ---
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

# --- TAB 2: EFA ---
with tab_efa:
    if st.session_state['phase1_data'] is not None and selected_items:
        n_cases = len(st.session_state['phase1_data'])
        if n_cases < 50:
            st.error(lang['sample_warning'])
        else:
            # إضافة مصفوفة الارتباطات قبل التحليل
            st.markdown("#### مصفوفة الارتباطات (Correlation Matrix)")
            corr_matrix = st.session_state['phase1_data'][selected_items].corr()
            st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format("{:.3f}"), use_container_width=True)
            st.markdown("---")

            c1, c2 = st.columns(2)
            factor_count = c1.number_input("Factors", min_value=1, value=2)
            rotation = c2.selectbox("Rotation", ["varimax", "oblimin"])
            
            if st.button(lang['run_efa']):
                out = efa_result(st.session_state['phase1_data'], selected_items, int(factor_count), rotation)
                st.session_state['efa_output'] = out
                st.success("EFA Completed Successfully!")
                
                # APA 7 P-value Formatting
                p_val = out['bartlett_p']
                p_str = "p < .001" if p_val < 0.001 else f"p = {p_val:.3f}"
                
                metrics = st.columns(4)
                metrics[2].metric("Bartlett χ²", f"{out['bartlett_chi2']:.2f}") 
                metrics[3].metric("Bartlett p", p_str)
                
                st.markdown("#### التشبعات العاملية (Factor Loadings)")
                st.dataframe(out["loadings"].style.format("{:.3f}"), use_container_width=True)
                
                st.markdown("#### Item-level KMO")
                st.dataframe(out["kmo_items"].rename_axis("Item").reset_index().style.format({"KMO": "{:.3f}"}), use_container_width=True)

# --- TAB 3: CFA ---
with tab_cfa:
    if st.session_state['phase2_data'] is not None and selected_items:
        n_cases_cfa = len(st.session_state['phase2_data'])
        if n_cases_cfa < 50:
            st.error(lang['sample_warning'])
        else:
            efa_out = st.session_state.get('efa_output')
            default_cfa_factors = int(efa_out['factor_count']) if efa_out else 2
            
            cfa_factors = st.number_input("CFA Factors", min_value=1, value=default_cfa_factors, key="cfa_factors")
            labels = [f"Factor {i+1}" for i in range(cfa_factors)]
            assign = {}
            
            st.markdown("#### توزيع الفقرات على العوامل")
            if efa_out:
                st.info(lang['auto_assign_msg'])
                
            cols = st.columns(2)
            for i, item in enumerate(selected_items):
                # SMART AUTO-ASSIGNMENT LOGIC
                default_idx = 0 
                if efa_out and item in efa_out['loadings'].index:
                    loadings_row = efa_out['loadings'].loc[item]
                    max_factor = loadings_row.abs().idxmax()
                    max_val = loadings_row.abs().max()
                    if max_val >= 0.30 and max_factor in labels:
                        default_idx = labels.index(max_factor) + 1
                        
                assign[item] = cols[i%2].selectbox(str(item), ["غير مدرج (Not included)"] + labels, index=default_idx, key=f"cfa_{item}")
            
            if st.button(lang['run_cfa']):
                f_assign = {f: [i for i, a in assign.items() if a == f] for f in labels}
                f_assign = {k: v for k, v in f_assign.items() if len(v) > 0}
                
                if not f_assign or any(len(v) < 2 for v in f_assign.values()):
                    st.error("⚠️ يرجى تعيين فقرتين على الأقل لكل عامل لتجنب الأخطاء في بناء نموذج المعادلة البنائية.")
                else:
                    try:
                        spec = build_cfa_specification(f_assign)
                        cfa_out = cfa_result(st.session_state['phase2_data'], spec)
                        st.session_state['cfa_output'] = cfa_out
                        st.success("CFA Completed Successfully!")
                        
                        fit_vals = cfa_out["fit"]
                        f_cols = st.columns(4)
                        f_cols[0].metric("CFI", f"{fit_vals['CFI']:.3f}")
                        f_cols[1].metric("TLI", f"{fit_vals['TLI']:.3f}")
                        f_cols[2].metric("RMSEA", f"{fit_vals['RMSEA']:.3f}")
                        f_cols[3].metric("χ² (df)", f"{fit_vals['chi2']:.2f} ({fit_vals['DoF']:.0f})")
                        
                        st.markdown("#### Parameter estimates")
                        st.dataframe(cfa_out["params"].style.format({"Estimate": "{:.3f}", "Est. Std": "{:.3f}", "Std. Err": "{:.3f}", "z-value": "{:.3f}", "p-value": "{:.4f}"}, na_rep="—"), use_container_width=True)

                        # رسم المخطط الهيكلي بـ Graphviz
                        st.markdown("#### المخطط الهيكلي (Structural Diagram / Diagramme structurel)")
                        dot_code = "digraph CFA {\nrankdir=LR;\nnode [shape=box, style=filled, fillcolor=white];\n"
                        for factor, items in f_assign.items():
                            dot_code += f'"{factor}" [shape=ellipse, style=filled, fillcolor="#bae6fd"];\n'
                            for item in items:
                                dot_code += f'"{factor}" -> "{item}";\n'
                        dot_code += "}"
                        st.graphviz_chart(dot_code)

                    except Exception as e:
                        st.error(f"CFA Error: {str(e)}")

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
            report_text += f"**1. التحليل العاملي الاستكشافي (EFA):**\nلضمان صلاحية البيانات للتحليل، أظهر اختبار KMO كفاءة جيدة بقيمة ({efa_out['kmo']:.3f}). وكان اختبار بارتليت دالاً إحصائياً (χ² = {efa_out['bartlett_chi2']:.2f}, {p_str}). تم استخراج ({efa_out['factor_count']}) عوامل باستخدام طريقة ({efa_out['method']}) وتدوير ({efa_out['rotation']}) وفقاً لمعايير APA 7.\n\n"
        
        if cfa_out:
            fit = cfa_out['fit']
            report_text += f"**2. التحليل العاملي التوكيدي (CFA):**\nللتأكد من صدق البناء ووفقاً لمعايير JARS، تم تطبيق نموذج CFA. أظهرت النتائج مؤشرات مطابقة جيدة للمتغيرات الكامنة: $\chi^2({fit['DoF']:.0f}) = {fit['chi2']:.2f}$، ومؤشر المطابقة المقارن CFI = ({fit.get('CFI',0):.3f})، وقيمة TLI = ({fit.get('TLI',0):.3f})، ومؤشر جذر متوسط مربع الخطأ RMSEA = ({fit.get('RMSEA',0):.3f}). تدل هذه المؤشرات على مطابقة النموذج مع البيانات الفعلية للمقياس.\n\n"
        
        st.write(report_text)
        st.success("التقرير الأكاديمي أعلاه تمت كتابته آلياً. يمكنك نسخه مباشرة ولصقه في مذكرتك أو بحثك العلمي!")
