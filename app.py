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

# --- Initialize Session State for Data Persistence & Feedback ---
if 'phase1_data' not in st.session_state:
    st.session_state['phase1_data'] = None
if 'phase2_data' not in st.session_state:
    st.session_state['phase2_data'] = None
if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = None
if 'feedback_submitted' not in st.session_state:
    st.session_state['feedback_submitted'] = False

st.set_page_config(
    page_title="PsychoStat Pro · Psychometric Analysis",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------ Multi-Language Dictionary ------------------
if 'lang' not in st.session_state:
    st.session_state.lang = 'العربية'

translations = {
    'English': {
        'select_lang': 'Select Language',
        'main_title': '💠 PsychoStat Pro',
        'subtitle': 'Explore the measurement quality of employee attitudes toward generative AI, with transparent samples, methods, and exportable results.',
        'developer': 'Platform Developer: Asmaa Dala',
        'adv_workspace': 'Advanced Study Workspace',
        'adv_desc': 'Upload pre-split Phase 1 & 2 files manually (for advanced users).',
        'data_org': 'How is your data organized?',
        'upload_device': 'Upload from device',
        'github_urls': 'Public GitHub URLs',
        'phase1_sample': 'Phase 1 - EFA sample',
        'phase2_sample': 'Phase 2 - CFA sample',
        'tab1': '📊 1. Raw Data & Descriptives',
        'tab2': '🔍 2. Exploratory Factor Analysis (EFA)',
        'tab3': '📈 3. Confirmatory Factor Analysis (CFA)',
        'tab4': '📄 4. Analysis Report',
        'raw_processing': 'Raw Survey Data Processing',
        'raw_info': 'Upload your raw survey data (Excel/CSV) directly from Google Forms to automatically extract demographic tables and split data for EFA/CFA.',
        'upload_forms': 'Upload Google Forms Data',
        'demo_summary': '1. Demographic Summary',
        'select_demo': 'Select Demographic Variables:',
        'normality_desc': '2. Normality & Descriptive Stats',
        'select_normality': 'Select Scale Items (for normality test):',
        'ready_split': 'Ready for Psychometric Analysis?',
        'split_btn': '✂️ Automatically Split Data for EFA & CFA (50/50)',
        'study_overview': 'Study Overview',
        'total_cases': 'Total available cases',
        'p1_cases': 'Phase 1 cases (EFA)',
        'p2_cases': 'Phase 2 cases (CFA)',
        'not_loaded': 'Not loaded',
        'case_study_title': '📖 Case Study: Employee Generative AI Attitude Scale (EGAIS) by Asmaa Dala',
        'case_study_desc': 'This scale is presented here as a demo to illustrate the platform\'s capabilities. You can use this platform to analyze your own survey data.',
        'case_study_body': """
        This scale (EGAIS) was developed specifically to measure employee attitudes toward generative AI in an actual work environment (an Algerian energy sector economic enterprise).
        
        **Summary of Psychometric Properties (Phase 1 - EFA):**
        * **Sample Size:** 150 employees.
        * **Extracted Factor Structure:** Two main dimensions (AI Anxiety and Perceived Efficacy).
        * **Explanatory Power:** The 23-item structure explains **67.045%** of the total variance.

        **⚠️ Phase 2 Results (CFA) - Notice for Researchers:**
        * Phase 2 (CFA) analyses revealed a **lack of full Discriminant Validity** between the dimensions.
        * **Practical Guidance:** Researchers are advised to account for the overlap between the two dimensions when using the scale.
        """,
        'feedback_title': '💬 Feedback & Consultations',
        'feedback_desc': 'Share your thoughts on PsychoStat Pro or request a consultation.',
        'feedback_rating': 'How was your experience?',
        'feedback_text': 'Leave a comment or question...',
        'feedback_submit': 'Send Feedback 🚀',
        'feedback_thanks': 'Thank you! Your feedback has been received. 😍'
    },
    'العربية': {
        'select_lang': 'اختر اللغة',
        'main_title': '💠 PsychoStat Pro',
        'subtitle': 'استكشف جودة قياس اتجاهات الموظفين نحو الذكاء الاصطناعي التوليدي، مع عينات وأساليب ونتائج علمية دقيقة وقابلة للتصدير.',
        'developer': 'مطورة المنصة: أسماء دالة',
        'adv_workspace': 'مساحة العمل المتقدمة',
        'adv_desc': 'رفع ملفات المرحلة 1 و 2 المقسمة مسبقاً يدوياً (للباحثين المتمرسين).',
        'data_org': 'كيف تنظم بياناتك؟',
        'upload_device': 'رفع من الجهاز',
        'github_urls': 'روابط غيت هاب العامة',
        'phase1_sample': 'عينة المرحلة 1 - التحليل الاستكشافي',
        'phase2_sample': 'عينة المرحلة 2 - التحليل التوكيدي',
        'tab1': '📊 1. البيانات الخام والإحصاء الوصفي',
        'tab2': '🔍 2. التحليل العاملي الاستكشافي (EFA)',
        'tab3': '📈 3. التحليل العاملي التوكيدي (CFA)',
        'tab4': '📄 4. تقرير التحليل',
        'raw_processing': 'معالجة بيانات الاستبيان الخام',
        'raw_info': 'قم برفع بيانات الاستبيان الخام (Excel/CSV) مباشرة من نماذج جوجل لاستخراج الجداول الديموغرافية تلقائياً وتقسيم البيانات لمرحلتي EFA و CFA.',
        'upload_forms': 'رفع بيانات نماذج جوجل',
        'demo_summary': '1. الملخص الديموغرافي',
        'select_demo': 'اختر المتغيرات الديموغرافية:',
        'normality_desc': '2. الإحصاء الوصفي والاعتدالية',
        'select_normality': 'اختر فقرات المقياس (لاختبار الاعتدالية):',
        'ready_split': 'هل أنت جاهز للتحليل السيكومتري؟',
        'split_btn': '✂️ تقسيم البيانات تلقائياً لـ EFA و CFA (بنسبة 50/50)',
        'study_overview': 'نظرة عامة على الدراسة',
        'total_cases': 'إجمالي الحالات المتاحة',
        'p1_cases': 'حالات المرحلة 1 (EFA)',
        'p2_cases': 'حالات المرحلة 2 (CFA)',
        'not_loaded': 'لم يتم التحميل',
        'case_study_title': '📖 مثال تطبيقي: تحليل مقياس (EGAIS) للباحثة أسماء دالة',
        'case_study_desc': 'هذا المقياس معروض هنا كنموذج (دراسة حالة) لتوضيح قدرة المنصة على استخراج الخصائص السيكومترية. يمكنك استخدام المنصة لتحليل بيانات استبيانك الخاص بكل حرية.',
        'case_study_body': """
        تم بناء وتطوير هذا المقياس (EGAIS) خصيصاً لقياس اتجاهات الموظفين نحو الذكاء الاصطناعي التوليدي في بيئة العمل الفعلية (مؤسسة اقتصادية بقطاع الطاقة الجزائري).
        
        **ملخص الخصائص السيكومترية (المرحلة 1 - التحليل الاستكشافي):**
        * **حجم العينة:** 150 موظفاً.
        * **الهيكل العاملي المستخرج:** بُعدان رئيسيان (القلق من الذكاء الاصطناعي، والفعالية المدركة).
        * **القوة التفسيرية:** يفسر الهيكل المكون من 23 فقرة **67.045%** من التباين الكلي.

        **⚠️ نتائج المرحلة 2 (التحليل التوكيدي) - ملاحظة للباحثين:**
        * كشفت تحليلات المرحلة 2 عن **عدم توفر الصدق التمييزي الكامل** بين البُعدين.
        * **توجيه عملي:** يُنصح الباحثون بأخذ التداخل بين البُعدين بعين الاعتبار عند استخدام المقياس في دراساتهم.
        """,
        'feedback_title': '💬 آراء ومقترحات الباحثين',
        'feedback_desc': 'يسعدنا سماع رأيك في منصة PsychoStat Pro أو ترك استشارتك.',
        'feedback_rating': 'كيف كانت تجربتك؟',
        'feedback_text': 'اكتب تعليقك أو استشارتك هنا...',
        'feedback_submit': 'إرسال التعليق 🚀',
        'feedback_thanks': 'شكراً لك! تم استلام رسالتك بنجاح. 😍'
    }
}

# Sidebar Language Selection
selected_language = st.sidebar.selectbox(
    translations[st.session_state.lang]['select_lang'],
    ['العربية', 'English'],
    index=['العربية', 'English'].index(st.session_state.lang)
)
st.session_state.lang = selected_language
lang_dict = translations[st.session_state.lang]

# --- Custom Global Styles (UI Improvements) ---
st.markdown("""
    <style>
    /* Force Buttons to be prominent and colorful */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important; /* Make buttons stretch nicely on mobile */
        border-color: #3b82f6 !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.4) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
        color: white !important;
        border-color: #60a5fa !important;
    }
    
    /* Prominent Case Study Card */
    .case-study-card {
        background: linear-gradient(to right, #f0f9ff, #e0f2fe);
        border: 2px solid #bae6fd;
        border-right: 8px solid #0284c7; /* Prominent accent color */
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.15);
    }
    .case-study-card h3 { 
        color: #0c4a6e; 
        margin-top: 0; 
        font-weight: 800;
        font-size: 1.3rem;
    }
    .case-study-card p {
        color: #0369a1;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Metric boxes improvements for mobile */
    [data-testid="stMetric"] { 
        background: #fff; 
        padding: 1rem; 
        border: 1px solid #e2e8f0; 
        border-radius: 12px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
    }
    </style>
    """, unsafe_allow_html=True)


# --- Helper Functions ---
SUPPORTED_TYPES = ["sav", "xlsx", "xls", "csv"]
TARGET_N_PER_PHASE = 150
MAX_GITHUB_FILE_BYTES = 50 * 1024 * 1024
PHASE_LABELS = {
    "phase1": "Phase 1 · EFA",
    "phase2": "Phase 2 · CFA & replication",
}

def read_uploaded_data(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".sav":
        with tempfile.NamedTemporaryFile(suffix=".sav") as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()
            data, _ = pyreadstat.read_sav(temp_file.name, apply_value_formats=False)
        return data
    if suffix in {".xlsx", ".xls"}:
        engine = "openpyxl" if suffix == ".xlsx" else "xlrd"
        return pd.read_excel(io.BytesIO(file_bytes), engine=engine)
    if suffix == ".csv":
        return pd.read_csv(io.BytesIO(file_bytes), sep=None, engine="python")
    raise ValueError(f"Unsupported file format: {suffix or 'unknown'}")

def normalize_public_github_url(url: str) -> tuple[str, str]:
    parsed = urlsplit(url.strip())
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("Enter a valid HTTPS GitHub file URL.") from error
    host = (parsed.hostname or "").lower()
    if (parsed.scheme != "https" or host not in {"github.com", "raw.githubusercontent.com"} or parsed.username or parsed.password or port not in (None, 443)):
        raise ValueError("Only public HTTPS GitHub file URLs are supported.")
    if parsed.query or parsed.fragment:
        raise ValueError("Remove query strings and fragments from the URL.")
    path_parts = [part for part in parsed.path.split("/") if part]
    if host == "github.com":
        if (len(path_parts) < 5 or path_parts[2] not in {"blob", "raw"} or not all(path_parts[:2])):
            raise ValueError("Use a GitHub file URL in the form github.com/owner/repository/blob/branch/path/file.sav")
        raw_path_parts = path_parts[:2] + path_parts[3:]
    else:
        if len(path_parts) < 4:
            raise ValueError("The raw GitHub URL must include owner, repository, branch, and file path.")
        raw_path_parts = path_parts
    file_name = unquote(raw_path_parts[-1])
    if Path(file_name).suffix.lower() not in {f".{kind}" for kind in SUPPORTED_TYPES}:
        raise ValueError("The GitHub file must end in .sav, .xlsx, .xls, or .csv.")
    encoded_path = "/".join(raw_path_parts)
    return f"https://raw.githubusercontent.com/{encoded_path}", file_name

def fetch_public_github_file(url: str) -> tuple[str, bytes]:
    raw_url, file_name = normalize_public_github_url(url)
    try:
        with requests.get(raw_url, headers={"User-Agent": "AttitudeLab-Psychometrics/1.0"}, timeout=(5, 20), allow_redirects=False, stream=True) as response:
            if 300 <= response.status_code < 400:
                raise ValueError("GitHub redirected this request. Paste the raw.githubusercontent.com URL instead.")
            if response.status_code != 200:
                raise ValueError(f"GitHub returned HTTP {response.status_code}.")
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_GITHUB_FILE_BYTES:
                raise ValueError("The file exceeds the 50 MB download limit.")
            contents = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk: continue
                contents.extend(chunk)
                if len(contents) > MAX_GITHUB_FILE_BYTES:
                    raise ValueError("The file exceeds the 50 MB download limit.")
    except requests.RequestException as error:
        raise ValueError("Could not reach the public GitHub file.") from error
    file_bytes = bytes(contents)
    if not file_bytes: raise ValueError("The GitHub file is empty.")
    if file_bytes.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("This URL returned a Git LFS pointer, not the dataset.")
    return file_name, file_bytes

def read_github_data(url: str, cache_key: str) -> pd.DataFrame:
    downloads = st.session_state.setdefault("_github_downloads", {})
    cached = downloads.get(cache_key)
    if cached is None or cached["url"] != url.strip():
        file_name, file_bytes = fetch_public_github_file(url)
        cached = {"url": url.strip(), "file_name": file_name, "file_bytes": file_bytes}
        downloads[cache_key] = cached
    return read_uploaded_data(cached["file_name"], cached["file_bytes"])

def numeric_item_columns(data: pd.DataFrame) -> list[str]:
    blocked = ("id", "participant", "respondent", "case", "index", "phase", "group")
    return [column for column in data.select_dtypes(include="number").columns if not any(token in str(column).lower() for token in blocked)]

def as_numeric_items(data: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    return data.loc[:, items].apply(pd.to_numeric, errors="coerce")

def descriptive_table(data: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    numeric = as_numeric_items(data, items)
    records = []
    for item in items:
        values = numeric[item].dropna()
        records.append({
            "Item": item, "Valid n": int(values.size),
            "Mean": values.mean() if not values.empty else np.nan,
            "SD": values.std(ddof=1) if values.size > 1 else np.nan,
            "Skewness": values.skew() if values.size > 2 else np.nan,
            "Kurtosis (excess)": values.kurtosis() if values.size > 3 else np.nan,
        })
    return pd.DataFrame(records)

def normality_table(data: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    numeric = as_numeric_items(data, items)
    records = []
    for item in items:
        values = numeric[item].dropna().to_numpy()
        if values.size < 3:
            w_value, p_value, note = np.nan, np.nan, "At least 3 valid observations required"
        elif np.unique(values).size < 2:
            w_value, p_value, note = np.nan, np.nan, "No variability"
        else:
            result = stats.shapiro(values)
            w_value, p_value = float(result.statistic), float(result.pvalue)
            note = "Shapiro–Wilk; p < .05 indicates evidence against normality"
            if values.size > 5000: note += "; SciPy cautions that p-values may be inaccurate above n=5,000"
        records.append({
            "Item": item, "Valid n": int(values.size), "Shapiro–Wilk W": w_value, "p-value": p_value,
            "Interpretation": ("Evidence against normality" if pd.notna(p_value) and p_value < 0.05 else "No evidence against normality" if pd.notna(p_value) else note),
            "Method note": note,
        })
    return pd.DataFrame(records)

def reliability_result(data: pd.DataFrame, items: list[str]) -> dict[str, Any]:
    numeric = as_numeric_items(data, items)
    complete = numeric.dropna(axis=0, how="any")
    result: dict[str, Any] = {
        "alpha": np.nan, "ci_low": np.nan, "ci_high": np.nan,
        "n_complete": int(len(complete)), "items": int(len(items)),
        "note": "Cronbach's alpha uses listwise-complete cases across selected items.",
    }
    if len(items) < 2:
        result["note"] = "At least two items are required."
        return result
    if len(complete) < 2:
        result["note"] = "At least two complete cases are required."
        return result
    alpha, interval = pg.cronbach_alpha(data=complete)
    result["alpha"] = float(alpha)
    result["ci_low"] = float(interval[0])
    result["ci_high"] = float(interval[1])
    return result

def efa_result(data: pd.DataFrame, items: list[str], factor_count: int, rotation: str) -> dict[str, Any]:
    numeric = as_numeric_items(data, items)
    complete = numeric.dropna(axis=0, how="any")
    if len(items) < 3: raise ValueError("Select at least 3 scale items for exploratory factor analysis.")
    if len(complete) <= len(items): raise ValueError(f"EFA needs more complete cases than selected items. Current complete-case n={len(complete)} and item count={len(items)}.")
    
    try:
        kmo_all, kmo_model = calculate_kmo(complete)
        bartlett_chi2, bartlett_p = calculate_bartlett_sphericity(complete)
    except Exception:
        kmo_all = np.full(len(items), np.nan)
        kmo_model = np.nan
        bartlett_chi2 = np.nan
        bartlett_p = np.nan

    kmo_items = pd.Series(kmo_all, index=items)
    fa = FactorAnalyzer(n_factors=factor_count, rotation=rotation, method='principal')
    fa.fit(complete)
    loadings = pd.DataFrame(fa.loadings_, index=items, columns=[f"Factor {i+1}" for i in range(factor_count)])
    ev, _ = fa.get_eigenvalues()
    eigenvalues_df = pd.DataFrame({"Component": range(1, len(ev) + 1), "Eigenvalue": ev})

    return {
        "n_complete": len(complete), "kmo": kmo_model, "kmo_items": kmo_items,
        "bartlett_chi2": bartlett_chi2, "bartlett_p": bartlett_p,
        "method": "PCA (Principal Component Analysis)", "rotation": rotation,
        "factor_count": factor_count, "loadings": loadings, "eigenvalues": eigenvalues_df
    }

def build_cfa_specification(factor_assignments: dict[str, list[str]]) -> dict[str, Any]:
    used_items = [item for factor_items in factor_assignments.values() for item in factor_items]
    if not used_items: raise ValueError("Assign at least three items to a CFA factor.")
    if len(used_items) != len(set(used_items)): raise ValueError("Each item can be assigned to only one factor in this simple-structure model.")
    for factor, factor_items in factor_assignments.items():
        if factor_items and len(factor_items) < 3: raise ValueError(f"{factor} has {len(factor_items)} item(s). Assign at least three indicators to each factor.")
    if any(not factor_items for factor_items in factor_assignments.values()): raise ValueError("Remove empty factors or assign items to each factor.")

    aliases: dict[str, str] = {}
    alias_to_item: dict[str, str] = {}
    for item in used_items:
        suffix_base = re.sub(r"[^A-Za-z0-9_]+", "_", str(item)).strip("_")
        base = f"item_{suffix_base or 'response'}"
        alias = base
        suffix = 2
        while alias in alias_to_item:
            alias = f"{base}_{suffix}"
            suffix += 1
        aliases[item] = alias
        alias_to_item[alias] = str(item)

    semopy_lines = []
    display_lines = []
    factor_aliases: dict[str, str] = {}
    for index, (factor, factor_items) in enumerate(factor_assignments.items(), start=1):
        factor_alias = f"F{index}"
        factor_aliases[factor_alias] = factor
        semopy_lines.append(f"{factor_alias} =~ " + " + ".join(aliases[item] for item in factor_items))
        display_lines.append(f"{factor} =~ " + " + ".join(map(str, factor_items)))

    return {
        "items": used_items, "aliases": aliases, "alias_to_item": alias_to_item,
        "factor_aliases": factor_aliases, "engine_syntax": "\n".join(semopy_lines),
        "display_syntax": "\n".join(display_lines),
    }

def cfa_result(data: pd.DataFrame, factor_assignments: dict[str, list[str]], specification: dict[str, Any]) -> dict[str, Any]:
    items = specification["items"]
    complete = as_numeric_items(data, items).dropna(axis=0, how="any")
    if len(complete) <= len(items): raise ValueError(f"CFA needs more complete cases than modeled items. Current complete-case n={len(complete)} and item count={len(items)}.")
    constant_items = [item for item in items if complete[item].nunique() < 2]
    if constant_items: raise ValueError("These modeled items have no variability among complete cases: " + ", ".join(map(str, constant_items)))
    renamed = complete.rename(columns=specification["aliases"])
    model = Model(specification["engine_syntax"])
    fit_result = model.fit(renamed, obj="MLW")
    if not fit_result.success: raise ValueError(f"The CFA optimizer did not converge: {fit_result.message or 'no convergence details returned'}")

    fit_table = calc_stats(model).iloc[0]
    fit_names = ["chi2", "DoF", "chi2 p-value", "CFI", "TLI", "RMSEA", "AIC", "BIC", "LogLik"]
    fit_values: dict[str, float] = {}
    for name in fit_names:
        value = fit_table.get(name, np.nan)
        fit_values[name] = float(value) if pd.notna(value) else np.nan

    parameters = model.inspect(std_est=True)
    for column in ("Estimate", "Est. Std", "Std. Err", "z-value", "p-value"):
        if column in parameters.columns: parameters[column] = pd.to_numeric(parameters[column], errors="coerce")
    for column in ("lval", "rval"):
        parameters[column] = parameters[column].replace({**specification["alias_to_item"], **specification["factor_aliases"]})
    parameters = parameters.rename(columns={"lval": "Left", "op": "Operator", "rval": "Right", "Estimate": "Estimate", "Est. Std": "Standardized estimate", "Std. Err": "SE", "z-value": "z", "p-value": "p"})

    return {
        "n_complete": int(len(complete)), "item_count": len(items), "factor_count": len(factor_assignments),
        "fit": fit_values, "parameters": parameters, "specification": specification,
        "estimator": "Maximum likelihood (MLW)", "assumption": "Selected item responses are treated as approximately continuous.",
    }

def add_report_rows(report_rows: list[dict[str, Any]], phase: str, metric: str, variable: str, value: Any, n_used: Any = "", notes: str = "") -> None:
    report_rows.append({"Phase": phase, "Metric": metric, "Variable": variable, "Value": value, "n used": n_used, "Notes": notes})

def add_phase_report(report_rows, phase, data, items, descriptives, normality, reliability) -> None:
    add_report_rows(report_rows, phase, "Sample size", "Rows in uploaded phase", int(len(data)), int(len(data)), f"Target n={TARGET_N_PER_PHASE}; check actual value against study plan.")
    for _, row in descriptives.iterrows():
        for metric in ("Valid n", "Mean", "SD", "Skewness", "Kurtosis (excess)"):
            add_report_rows(report_rows, phase, metric, str(row["Item"]), row[metric], row["Valid n"], "Kurtosis is reported as excess kurtosis (normal distribution = 0).")
    for _, row in normality.iterrows():
        for metric in ("Shapiro–Wilk W", "p-value"):
            add_report_rows(report_rows, phase, metric, str(row["Item"]), row[metric], row["Valid n"], str(row["Method note"]))
    for metric, value in (("Cronbach's alpha", reliability["alpha"]), ("Alpha CI lower", reliability["ci_low"]), ("Alpha CI upper", reliability["ci_high"])):
        add_report_rows(report_rows, phase, metric, "Selected scale items", value, reliability["n_complete"], reliability["note"])

def render_distribution(data: pd.DataFrame, item: str, phase_name: str) -> None:
    values = pd.to_numeric(data[item], errors="coerce").dropna().to_numpy()
    if values.size < 3 or np.unique(values).size < 2:
        st.info("At least three valid, non-constant responses are needed for a distribution plot.")
        return
    figure, axes = plt.subplots(1, 2, figsize=(10, 3.5))
    figure.patch.set_facecolor("#ffffff")
    axes[0].hist(values, bins="auto", color="#4c8ed9", edgecolor="white", alpha=0.9)
    axes[0].axvline(np.mean(values), color="#e89245", linewidth=2, label="Mean")
    axes[0].set_title("Observed response distribution")
    axes[0].set_xlabel("Response")
    axes[0].set_ylabel("Frequency")
    axes[0].legend(frameon=False)
    stats.probplot(values, dist="norm", plot=axes[1])
    axes[1].get_lines()[0].set_markerfacecolor("#4c8ed9")
    axes[1].get_lines()[0].set_markeredgecolor("#4c8ed9")
    axes[1].get_lines()[1].set_color("#e89245")
    axes[1].set_title("Normal Q–Q plot")
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines[["left", "bottom"]].set_color("#d8e2eb")
        axis.tick_params(colors="#687b8e")
        axis.title.set_color("#17324d")
    figure.suptitle(f"{phase_name} · {item}", color="#17324d", fontweight="bold")
    figure.tight_layout()
    st.pyplot(figure, width="stretch")
    plt.close(figure)

def show_sample_note(data: pd.DataFrame, phase_key: str) -> None:
    n = len(data)
    if n == TARGET_N_PER_PHASE:
        st.success(f"{PHASE_LABELS[phase_key]} contains the planned {TARGET_N_PER_PHASE} cases.")
    else:
        st.warning(f"{PHASE_LABELS[phase_key]} contains {n} rows; the study plan specifies {TARGET_N_PER_PHASE}.")

# --- Modern Header ---
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); padding: 45px 30px; border-radius: 20px; text-align: center; color: white; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.4); margin-bottom: 30px;">
        <h1 style="color: #ffffff; margin: 0; font-size: 48px; font-weight: 900; letter-spacing: 1.5px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
            {lang_dict.get('main_title')}
        </h1>
        <p style="font-size: 18px; margin: 15px auto 0 auto; max-width: 800px; opacity: 0.95; line-height: 1.6;">
            {lang_dict.get('subtitle')}
        </p>
        <div style="margin-top: 25px; display: inline-block; background: rgba(255, 255, 255, 0.15); padding: 8px 24px; border-radius: 50px; font-size: 15px; font-weight: 600; backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.2);">
            👩‍💻 {lang_dict.get('developer')}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Prominent "Scale Guide" Integration (Demo Case Study) ---
st.markdown(f"""
    <div class="case-study-card">
        <h3>{lang_dict.get('case_study_title')}</h3>
        <p>{lang_dict.get('case_study_desc')}</p>
    </div>
""", unsafe_allow_html=True)
with st.expander("🔍 " + lang_dict.get('select_lang') + " / عرض تفاصيل المقياس", expanded=False):
    st.markdown(lang_dict.get('case_study_body'))


# --- Sidebar: Advanced Data Uploader ---
with st.sidebar:
    st.markdown(f"### {lang_dict.get('adv_workspace')}")
    st.caption(lang_dict.get('adv_desc'))
    st.markdown("---")
    source_mode = st.radio(lang_dict.get('data_org'), [lang_dict.get('upload_device'), lang_dict.get('github_urls')])
    
    if source_mode == lang_dict.get('upload_device'):
        phase1_file = st.file_uploader(lang_dict.get('phase1_sample'), type=SUPPORTED_TYPES, key="phase1_upload")
        phase2_file = st.file_uploader(lang_dict.get('phase2_sample'), type=SUPPORTED_TYPES, key="phase2_upload")
        for uploaded, label in ((phase1_file, "Phase 1"), (phase2_file, "Phase 2")):
            if uploaded is not None:
                try:
                    loaded = read_uploaded_data(uploaded.name, uploaded.getvalue())
                    if label == "Phase 1":
                        st.session_state['phase1_data'] = loaded
                    else:
                        st.session_state['phase2_data'] = loaded
                except Exception as error:
                    st.error(f"Could not read the {label} file: {error}")
    else:
        st.caption("Paste public GitHub raw URLs.")
        phase1_url = st.text_input("Phase 1 URL", placeholder="https://raw.github.com...", key="phase1_github_url")
        phase2_url = st.text_input("Phase 2 URL", placeholder="https://raw.github.com...", key="phase2_github_url")
        for url, label, cache_key in ((phase1_url, "Phase 1", "phase1"), (phase2_url, "Phase 2", "phase2")):
            if url.strip():
                try:
                    with st.spinner(f"Fetching {label}..."):
                        loaded = read_github_data(url, cache_key)
                        if label == "Phase 1":
                            st.session_state['phase1_data'] = loaded
                        else:
                            st.session_state['phase2_data'] = loaded
                except Exception as error:
                    st.error(f"Could not load the {label} GitHub file: {error}")

# Determine available data globally
available_data = [d for d in (st.session_state['phase1_data'], st.session_state['phase2_data'], st.session_state['raw_data']) if d is not None]

# --- Global Item Selection ---
selected_items = []
if available_data:
    common_columns = set(available_data[0].columns)
    for data in available_data[1:]:
        common_columns &= set(data.columns)
    
    excluded_keywords = ['id', 'participant', 'case', 'total', 'gender', 'sex', 'الجنس', 'المجموع']
    numeric_items = [col for col in available_data[0].select_dtypes(include=[np.number]).columns if col in common_columns and not any(kw in str(col).lower() for kw in excluded_keywords)]
    
    if numeric_items:
        default_items = [col for col in numeric_items if str(col).lower().startswith('s') and str(col).lower() not in ["some", "some1", "some2"]]
        if not default_items: default_items = numeric_items[:min(10, len(numeric_items))]
        selected_items = st.multiselect("📌 " + lang_dict.get('select_normality').split('(')[0], options=numeric_items, default=default_items, format_func=str)

# --- Main Workspace Tabs ---
tab_desc, tab_efa, tab_cfa, tab_report = st.tabs([
    lang_dict.get('tab1'), 
    lang_dict.get('tab2'), 
    lang_dict.get('tab3'),
    lang_dict.get('tab4')
])

# Variables to hold states for the report
report_rows = []
efa_output = None
cfa_output = None
cfa_error = None

# ==========================================
# TAB 1: DESCRIPTIVE STATS & RAW DATA
# ==========================================
with tab_desc:
    st.markdown(f"#### {lang_dict.get('raw_processing')}")
    st.info(lang_dict.get('raw_info'))
    
    raw_file = st.file_uploader(lang_dict.get('upload_forms'), type=["csv", "xlsx", "xls"], key="raw_data_uploader")
    
    if raw_file is not None:
        if raw_file.name.endswith('.csv'):
            df_raw = pd.read_csv(raw_file)
        else:
            df_raw = pd.read_excel(raw_file)
            
        st.session_state['raw_data'] = df_raw
        st.success(f"✅ Data loaded successfully! Total responses: **{len(df_raw)}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{lang_dict.get('demo_summary')}**")
            demo_cols = st.multiselect(lang_dict.get('select_demo'), df_raw.columns, key="demo_cols")
            if demo_cols:
                for col in demo_cols:
                    st.write(f"**{col}**")
                    freq_df = df_raw[col].value_counts().reset_index()
                    freq_df.columns = [col, 'Frequency']
                    freq_df['Percentage (%)'] = (freq_df['Frequency'] / len(df_raw) * 100).round(2)
                    st.dataframe(freq_df, use_container_width=True)
                    
        with col2:
            st.markdown(f"**{lang_dict.get('normality_desc')}**")
            item_cols = st.multiselect(lang_dict.get('select_normality'), df_raw.columns, key="item_cols_desc", default=selected_items if selected_items else None)
            if item_cols:
                desc_df = df_raw[item_cols].describe().T[['mean', 'std']].round(3)
                desc_df['Skewness'] = df_raw[item_cols].skew().round(3)
                desc_df['Kurtosis'] = df_raw[item_cols].kurtosis().round(3)
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
    phase1_data = st.session_state['phase1_data']
    st.markdown(f"#### {lang_dict.get('phase1_efa')}")
    
    if phase1_data is None:
        st.info("Upload data in the first tab and click 'Split', or upload a Phase 1 file in the sidebar.")
    elif not selected_items:
        st.warning("Please select scale items above the tabs first.")
    else:
        show_sample_note(phase1_data, "phase1")
        phase1_descriptives = descriptive_table(phase1_data, selected_items)
        phase1_normality = normality_table(phase1_data, selected_items)
        phase1_reliability = reliability_result(phase1_data, selected_items)
        add_phase_report(report_rows, PHASE_LABELS["phase1"], phase1_data, selected_items, phase1_descriptives, phase1_normality, phase1_reliability)
        
        try:
            complete = as_numeric_items(phase1_data, selected_items).dropna()
            if len(selected_items) < 3:
                raise ValueError("Select at least 3 scale items for exploratory factor analysis.")
            if len(complete) <= len(selected_items):
                raise ValueError(f"Current complete-case n={len(complete)} is not greater than the number of items ({len(selected_items)}).")
            if any(complete[item].nunique() < 2 for item in selected_items):
                constant = [item for item in selected_items if complete[item].nunique() < 2]
                raise ValueError("Items with no variability must be corrected or removed: " + ", ".join(map(str, constant)))
            
            eigenvalues = np.linalg.eigvalsh(complete.corr().to_numpy())[::-1]
            suggested_factors = int((eigenvalues > 1).sum())
            max_factors = max(1, len(selected_items) - 1)
            recommended = min(max(1, suggested_factors), max_factors)
            
            controls = st.columns(2)
            with controls[0]:
                factor_count = st.number_input("Factors to retain", min_value=1, max_value=max_factors, value=recommended, step=1)
            with controls[1]:
                rotation = st.selectbox("Rotation", ["varimax"])
            
            efa_output = efa_result(phase1_data, selected_items, int(factor_count), rotation)
            
            metrics = st.columns(4)
            metrics[2].metric("Bartlett χ²", f"{efa_output['bartlett_chi2']:.2f}") 
            metrics[3].metric("Bartlett p", f"{efa_output['bartlett_p']:.4g}")
            
            st.markdown("#### Eigenvalues")
            st.dataframe(efa_output["eigenvalues"].style.format({"Eigenvalue": "{:.3f}"}), width="stretch", hide_index=True)
            
            st.markdown("#### Factor loadings")
            st.dataframe(efa_output["loadings"].style.format("{:.3f}"), width="stretch")
            
            st.markdown("#### Scale Reliability Metrics (Cronbach's α & McDonald's ω)")
            st.dataframe(pd.DataFrame([{"Component / Scale": "Overall Scale", "Metric Type": "Cronbach's Alpha", "Value": phase1_reliability.get("alpha", 0)}] + [{"Component / Scale": col, "Metric Type": "McDonald's Omega", "Value": (efa_output["loadings"][col].sum()**2) / ((efa_output["loadings"][col].sum()**2) + (1 - efa_output["loadings"][col]**2).sum())} for col in efa_output["loadings"].columns]).style.format({"Value": "{:.3f}"}), width="stretch", hide_index=True)
            
            st.markdown("#### Item-level KMO")
            st.dataframe(efa_output["kmo_items"].rename_axis("Item").reset_index().style.format({"KMO": "{:.3f}"}), width="stretch", hide_index=True)
            
            for _, row in efa_output["eigenvalues"].iterrows():
                add_report_rows(report_rows, PHASE_LABELS["phase1"], "Correlation-matrix eigenvalue", row["Component"], row["Eigenvalue"], efa_output["n_complete"], "Kaiser > 1 shown as a heuristic only.")
            add_report_rows(report_rows, PHASE_LABELS["phase1"], "Overall KMO", "Selected scale items", efa_output["kmo"], efa_output["n_complete"], "Kaiser-Meyer-Olkin measure.")
            add_report_rows(report_rows, PHASE_LABELS["phase1"], "Bartlett's test chi-square", "Correlation matrix", efa_output["bartlett_chi2"], efa_output["n_complete"], "Bartlett test.")
            add_report_rows(report_rows, PHASE_LABELS["phase1"], "Bartlett's test p-value", "Correlation matrix", efa_output["bartlett_p"], efa_output["n_complete"], "Bartlett test.")
            
            for item, loading_row in efa_output["loadings"].iterrows():
                for factor, loading in loading_row.items():
                    add_report_rows(report_rows, PHASE_LABELS["phase1"], "Factor loading", f"{item} · {factor}", loading, efa_output["n_complete"], f"{efa_output['method']}; {efa_output['rotation']} rotation.")
        except Exception as error:
            st.error(f"EFA could not be completed: {error}")

        st.markdown("#### Phase 1 descriptive statistics")
        st.dataframe(phase1_descriptives.style.format({"Mean": "{:.3f}", "SD": "{:.3f}", "Skewness": "{:.3f}", "Kurtosis (excess)": "{:.3f}"}), width="stretch", hide_index=True)
        
        st.markdown("#### Phase 1 normality checks")
        st.dataframe(phase1_normality.style.format({"Shapiro–Wilk W": "{:.4f}", "p-value": "{:.4g}"}), width="stretch", hide_index=True)
        
        phase1_plot_item = st.selectbox("Inspect a Phase 1 item distribution", options=selected_items, key="phase1_plot_item")
        render_distribution(phase1_data, phase1_plot_item, PHASE_LABELS["phase1"])


# ==========================================
# TAB 3: CONFIRMATORY FACTOR ANALYSIS (CFA)
# ==========================================
with tab_cfa:
    phase2_data = st.session_state['phase2_data']
    st.markdown(f"#### {lang_dict.get('phase2_cfa')}")
    
    if phase2_data is None:
        st.info("Upload data in the first tab and click 'Split', or upload a Phase 2 file in the sidebar.")
    elif not selected_items:
        st.warning("Please select scale items above the tabs first.")
    else:
        show_sample_note(phase2_data, "phase2")
        phase2_descriptives = descriptive_table(phase2_data, selected_items)
        phase2_normality = normality_table(phase2_data, selected_items)
        phase2_reliability = reliability_result(phase2_data, selected_items)
        add_phase_report(report_rows, PHASE_LABELS["phase2"], phase2_data, selected_items, phase2_descriptives, phase2_normality, phase2_reliability)
        
        st.markdown("---")
        st.markdown("### Specify the Phase 2 measurement model")
        if efa_output is not None:
            st.info("Starting assignments are suggested from Phase 1 EFA loadings. Review them before fitting.")
        
        max_cfa_factors = max(1, min(6, len(selected_items) // 3))
        suggested_cfa_factors = min(max(1, int(efa_output["factor_count"])), max_cfa_factors) if efa_output is not None else 1
        
        cfa_items_key = hashlib.sha1("|".join(map(str, selected_items)).encode("utf-8")).hexdigest()[:10]
        
        is_my_demo_scale = "s2" in selected_items and "s30" in selected_items
        forced_cfa_factors = 1 if is_my_demo_scale else suggested_cfa_factors

        cfa_factor_count = st.number_input("Number of CFA factors", min_value=1, max_value=max_cfa_factors, value=forced_cfa_factors, step=1, key=f"cfa_factor_count_{cfa_items_key}")
        cfa_factor_labels = [f"Factor {index + 1}" for index in range(cfa_factor_count)]
        
        default_assignment_by_item = {item: (cfa_factor_labels[0] if not efa_output else "Not included") for item in selected_items}
        if efa_output is not None:
            efa_loadings = efa_output["loadings"]
            for item in selected_items:
                if item not in efa_loadings.index: continue
                item_loadings = efa_loadings.loc[item]
                strongest_factor = item_loadings.abs().idxmax()
                if strongest_factor in cfa_factor_labels and abs(float(item_loadings[strongest_factor])) >= 0.30:
                    default_assignment_by_item[item] = strongest_factor

        st.markdown("#### Assign items to factors")
        assignment_columns = st.columns(2)
        assignment_by_item: dict[str, str] = {}
        select_options = ["Not included", *cfa_factor_labels]
        
        for item_index, item in enumerate(selected_items):
            default_assignment = default_assignment_by_item[item]
            if "s2" in selected_items and "s30" in selected_items and cfa_factor_count == 1:
                default_assignment = "Factor 1"
            if default_assignment not in select_options:
                default_assignment = "Not included"
            
            with assignment_columns[item_index % 2]:
                assignment_by_item[item] = st.selectbox(
                    str(item), options=select_options, index=select_options.index(default_assignment),
                    key=("cfa_assignment_" + hashlib.sha1(str(item).encode("utf-8")).hexdigest()[:10] + f"_{cfa_factor_count}")
                )

        factor_assignments = {factor: [item for item, assigned_factor in assignment_by_item.items() if assigned_factor == factor] for factor in cfa_factor_labels}
        
        cfa_specification, cfa_validation_error = None, None
        try:
            cfa_specification = build_cfa_specification(factor_assignments)
        except ValueError as error:
            cfa_validation_error = str(error)

        if cfa_validation_error: st.warning(cfa_validation_error)
        if len(selected_items) < 3:
            cfa_validation_error = "Select at least three scale items before fitting a CFA."
            st.warning(cfa_validation_error)

        if cfa_specification is not None:
            cfa_complete_for_signature = as_numeric_items(phase2_data, cfa_specification["items"]).dropna(axis=0, how="any")
            cfa_data_digest = hashlib.sha256(pd.util.hash_pandas_object(cfa_complete_for_signature, index=True).values.tobytes()).hexdigest()
            cfa_signature = hashlib.sha256((cfa_data_digest + cfa_specification["engine_syntax"] + "MLW").encode("utf-8")).hexdigest()
            
            fit_cfa = st.button("Fit Phase 2 CFA", type="primary", key="fit_phase2_cfa", disabled=bool(cfa_validation_error))
            
            if fit_cfa:
                try:
                    with st.spinner("Fitting the Phase 2 CFA model…"):
                        fitted_cfa = cfa_result(phase2_data, factor_assignments, cfa_specification)
                    st.session_state["_cfa_fit_result"] = {"signature": cfa_signature, "result": fitted_cfa, "error": None}
                except Exception as error:
                    st.session_state["_cfa_fit_result"] = {"signature": cfa_signature, "result": None, "error": str(error)}

            cached_cfa = st.session_state.get("_cfa_fit_result")
            if cached_cfa and cached_cfa["signature"] == cfa_signature:
                cfa_output = cached_cfa["result"]
                cfa_error = cached_cfa["error"]

            if cfa_error:
                st.error(f"CFA could not be completed: {cfa_error}")
            elif cfa_output:
                st.markdown("#### Model fit")
                def cfa_metric(value: float, digits: int = 3) -> str:
                    return f"{value:.{digits}f}" if np.isfinite(value) else "—"

                fit_values = cfa_output["fit"]
                fit_metrics = st.columns(4)
                fit_metrics[0].metric("CFI", cfa_metric(fit_values["CFI"]))
                fit_metrics[1].metric("TLI", cfa_metric(fit_values["TLI"]))
                fit_metrics[2].metric("RMSEA", cfa_metric(fit_values["RMSEA"]))
                fit_metrics[3].metric("χ² (df)", f"{cfa_metric(fit_values['chi2'], 2)} ({cfa_metric(fit_values['DoF'], 0)})")
                
                st.markdown("#### Parameter estimates")
                st.dataframe(cfa_output["parameters"].style.format({"Estimate": "{:.3f}", "Standardized estimate": "{:.3f}", "SE": "{:.3f}", "z": "{:.3f}", "p": "{:.4g}"}, na_rep="—"), width="stretch", hide_index=True)
                
                st.markdown("#### Convergent Validity (CR & AVE)")
                try:
                    loadings = cfa_output["parameters"]
                    std_loadings = pd.to_numeric(loadings[loadings['Operator'] == '~']['Standardized estimate'], errors='coerce')  
                    sum_loadings_sq = (std_loadings.sum())**2  
                    sum_sq_loadings = (std_loadings**2).sum()  
                    sum_errors = (1 - std_loadings**2).sum()   
                    
                    cr_value = sum_loadings_sq / (sum_loadings_sq + sum_errors)
                    ave_value = sum_sq_loadings / len(std_loadings)
                    
                    construct_name = "General Attitude towards AI" if is_my_demo_scale else "Factor 1"
                    validity_df = pd.DataFrame({
                        "Construct": [construct_name],
                        "Composite Reliability (CR)": [f"{cr_value:.3f}"],
                        "Average Variance Extracted (AVE)": [f"{ave_value:.3f}"],
                        "Interpretation": ["Good" if ave_value >= 0.50 and cr_value >= 0.70 else "Needs Review"]
                    })
                    st.dataframe(validity_df, width="stretch", hide_index=True)
                except Exception as e:
                    st.info("Could not calculate CR and AVE.")

                if cfa_factor_count > 1:
                    st.markdown("#### Discriminant Validity (Fornell-Larcker Criterion)")
                    try:
                        loadings_df = cfa_output["parameters"]
                        loadings_df['Standardized estimate'] = pd.to_numeric(loadings_df['Standardized estimate'], errors='coerce')
                        factors_list = loadings_df[loadings_df['Operator'] == '~']['Left'].unique()
                        ave_dict = {}
                        for f in factors_list:
                            f_loadings = loadings_df[(loadings_df['Operator'] == '~') & (loadings_df['Left'] == f)]['Standardized estimate'].astype(float)
                            if len(f_loadings) > 0:
                                ave_dict[f] = (f_loadings**2).sum() / len(f_loadings)
                        
                        correlations = loadings_df[(loadings_df['Operator'] == '~~') & (loadings_df['Left'] != loadings_df['Right'])]
                        if not correlations.empty:
                            disc_results = []
                            for _, row in correlations.iterrows():
                                f1, f2 = row['Left'], row['Right']
                                if f1 in ave_dict and f2 in ave_dict:
                                    corr_val = abs(float(row['Standardized estimate']))
                                    sqrt_ave_f1, sqrt_ave_f2 = ave_dict[f1] ** 0.5, ave_dict[f2] ** 0.5
                                    passed = (corr_val < sqrt_ave_f1) and (corr_val < sqrt_ave_f2)
                                    disc_results.append({
                                        "Pair": f"{f1} ↔ {f2}", "Correlation": f"{corr_val:.3f}",
                                        f"Sqrt AVE ({f1})": f"{sqrt_ave_f1:.3f}", f"Sqrt AVE ({f2})": f"{sqrt_ave_f2:.3f}",
                                        "Status": "Achieved" if passed else "Not Achieved"
                                    })
                            if disc_results:
                                st.dataframe(pd.DataFrame(disc_results), width="stretch", hide_index=True)
                        else:
                            st.info("No inter-factor correlations found.")
                    except Exception as e:
                        st.info("Could not calculate Discriminant Validity.")

                for metric_name, metric_value in fit_values.items():
                    add_report_rows(report_rows, PHASE_LABELS["phase2"], f"CFA {metric_name}", "Measurement model", metric_value, cfa_output["n_complete"], cfa_output["assumption"])
                for _, parameter in cfa_output["parameters"].iterrows():
                    parameter_name = f"{parameter['Left']} {parameter['Operator']} {parameter['Right']}"
                    for estimate_name in ("Estimate", "Standardized estimate", "SE", "z", "p"):
                        add_report_rows(report_rows, PHASE_LABELS["phase2"], f"CFA parameter {estimate_name}", parameter_name, parameter[estimate_name], cfa_output["n_complete"], cfa_output["estimator"])

# ==========================================
# TAB 4: ANALYSIS REPORT & EXPORT
# ==========================================
with tab_report:
    st.markdown("### Open analysis report")
    st.caption("A tidy, machine-readable CSV containing descriptive, reliability, EFA, and CFA results.")
    
    add_report_rows(report_rows, "Study", "Scale", "Instrument", "Employee Attitudes toward Generative AI", "", f"Selected items: {', '.join(map(str, selected_items))}")
    
    report = pd.DataFrame(report_rows)
    if not report.empty:
        report_view = report.copy()
        for column in ("Value", "n used"):
            if column in report_view:
                report_view[column] = report_view[column].map(lambda value: "" if pd.isna(value) else str(value))
        st.dataframe(report_view, width="stretch", hide_index=True)
        st.download_button("Download analysis report · CSV", data=report.to_csv(index=False).encode("utf-8-sig"), file_name="psychometric_report.csv", mime="text/csv", type="primary")
    else:
        st.info("Process data in the previous tabs to generate the analysis report.")

    if cfa_output is not None:
        st.markdown("#### Automated APA 7 Results Draft")
        try:
            fit_data = cfa_output.get("fit", None)
            chi2_val = fit_data.get("chi2", 0.0)
            df_val = fit_data.get("DoF", 0.0)
            p_val = fit_data.get("chi2 p-value", 0.0)
            cfi_val = fit_data.get("CFI", 0.0)
            tli_val = fit_data.get("TLI", 0.0)
            rmsea_val = fit_data.get("RMSEA", 0.0)
            
            apa_template = f"""
**Confirmatory Factor Analysis (CFA) Results:**

A Confirmatory Factor Analysis was conducted to evaluate the measurement model. The goodness-of-fit indices indicated the following: $\\chi^2({df_val:.0f}) = {chi2_val:.2f}, p = {p_val:.3f}$. The Comparative Fit Index (CFI) was {cfi_val:.3f}, and the Tucker-Lewis Index (TLI) was {tli_val:.3f}. The Root Mean Square Error of Approximation (RMSEA) was {rmsea_val:.3f}.
            """
            st.info(apa_template)
        except Exception as e:
            st.info("Run Phase 2 CFA to generate the automated APA 7 results draft.")

    # --- Interactive Feedback Section ---
    st.markdown("---")
    st.markdown(f"### {lang_dict.get('feedback_title')}")
    st.caption(lang_dict.get('feedback_desc'))
    
    if not st.session_state['feedback_submitted']:
        with st.form("feedback_form"):
            st.radio(lang_dict.get('feedback_rating'), ["😍 ممتاز", "👍 جيد جداً", "🤔 يحتاج تحسين"], horizontal=True)
            st.text_area(lang_dict.get('feedback_text'), height=100)
            submitted = st.form_submit_button(lang_dict.get('feedback_submit'))
            
            if submitted:
                st.session_state['feedback_submitted'] = True
                st.rerun()
    else:
        st.success(lang_dict.get('feedback_thanks'))
        if st.button("إرسال رسالة أخرى"):
            st.session_state['feedback_submitted'] = False
            st.rerun()
