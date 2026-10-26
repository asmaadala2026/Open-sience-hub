from __future__ import annotations
import sklearn.utils
import sklearn.utils.validation
if not hasattr(sklearn.utils, 'force_all_finite'):
    sklearn.utils.force_all_finite = True
if not hasattr(sklearn.utils.validation, 'force_all_finite'):
    sklearn.utils.validation.force_all_finite = True
    



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
phase1_data = None
phase2_data = None

st.set_page_config(
    page_title="Attitude Lab · Psychometric Analysis",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ------------------ Multi-Language & Developer Settings ------------------
if 'lang' not in st.session_state:
    st.session_state.lang = 'English'

translations = {
    'English': {
        'developer': "👩‍💻 Platform Developer: Asmaa Dala",
        'select_lang': "Select Language",
        'main_title': "Attitude Lab",
        'subtitle': "Explore the measurement quality of employee attitudes toward generative AI...",
        'start_text': "Start with your study data"
    },
    'العربية': {
        'developer': "👩‍💻 مطورة المنصة: الطالبة أسماء دالة",
        'select_lang': "اختر اللغة",
        'main_title': "مختبر الاتجاهات (Attitude Lab)",
        'subtitle': "استكشف جودة قياس اتجاهات الموظفين نحو الذكاء الاصطناعي التوليدي...",
        'start_text': "ابدأ ببيانات دراستك"
    },
    'Français': {
        'developer': "👩‍💻 Développeuse: Asmaa Dala",
        'select_lang': "Choisir la langue",
        'main_title': "Attitude Lab",
        'subtitle': "Explorez la qualité de la mesure des attitudes des employés envers l'IA générative...",
        'start_text': "Commencez avec vos données d'étude"
    }
}

# Add language selection dropdown at the top of the sidebar
selected_language = st.sidebar.selectbox(
    translations[st.session_state.lang]['select_lang'],
    ['English', 'العربية', 'Français'],
    index=['English', 'العربية', 'Français'].index(st.session_state.lang)
)
st.session_state.lang = selected_language
lang_dict = translations[st.session_state.lang]

# Display your name as the developer in a beautifully styled sidebar card
st.sidebar.markdown(f"""
<div style="background-color: #f0f2f6; padding: 12px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #d1d5db; text-align: center;">
    <h4 style="margin: 0; color: #1f2937; font-family: sans-serif; font-size: 14px;">{lang_dict['developer']}</h4>
</div>
""", unsafe_allow_html=True)



st.markdown(
    """
    <style>
    :root {
      --ink: #17324d;
      --muted: #687b8e;
      --blue: #3378c6;
      --blue-soft: #eaf3ff;
      --orange: #e89245;
      --orange-soft: #fff3e7;
      --green: #419b78;
      --green-soft: #eaf7f0;
      --line: #e6edf3;
      --canvas: #f6f9fc;
    }
    .stApp { background: var(--canvas); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(246, 249, 252, .9); }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }
    [data-testid="stMainBlockContainer"] { padding-top: 1.65rem; padding-bottom: 3rem; max-width: 1440px; }
    h1, h2, h3 { color: var(--ink); letter-spacing: -.025em; }
    h1 { font-size: 2.25rem !important; font-weight: 750 !important; }
    h2 { font-size: 1.45rem !important; font-weight: 700 !important; }
    h3 { font-size: 1.08rem !important; font-weight: 700 !important; }
    [data-testid="stMetric"] {
      background: #fff; padding: 1rem 1.1rem; border: 1px solid var(--line);
      border-radius: 16px; box-shadow: 0 5px 20px rgba(35, 72, 105, .045);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: .82rem; }
    [data-testid="stMetricValue"] { color: var(--ink); font-weight: 740; }
    [data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 7px; border-bottom: 1px solid var(--line); }
    [data-testid="stTabs"] button[data-baseweb="tab"] {
      border-radius: 10px 10px 0 0; color: var(--muted); font-weight: 650;
      padding: .65rem 1rem; background: transparent;
    }
    [data-testid="stTabs"] button[aria-selected="true"] { color: var(--blue); background: var(--blue-soft); }
    div[data-testid="stAlert"] { border-radius: 12px; }
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
    .eyebrow {
      text-transform: uppercase; color: var(--blue); letter-spacing: .12em;
      font-size: .73rem; font-weight: 800; margin-bottom: .28rem;
    }
    .hero {
      padding: 1.55rem 1.8rem; border: 1px solid #dce8f3; border-radius: 20px;
      background: linear-gradient(115deg, #fff 0%, #f0f7ff 61%, #f4fbf7 100%);
      margin-bottom: 1.2rem;
    }
    .hero p { color: var(--muted); margin: .2rem 0 0; font-size: 1rem; }
    .section-card {
      background: #fff; border: 1px solid var(--line); border-radius: 16px;
      padding: 1rem 1.15rem; margin: .5rem 0 1rem;
    }
    .section-card p { color: var(--muted); margin: .25rem 0 0; font-size: .92rem; }
    .pill {
      display: inline-block; padding: .24rem .65rem; border-radius: 999px;
      background: var(--green-soft); color: #267653; font-size: .75rem;
      font-weight: 750; margin-right: .35rem;
    }
    .muted { color: var(--muted); }
    .small-note { color: var(--muted); font-size: .82rem; }
    .stButton > button, .stDownloadButton > button {
      border-radius: 10px; font-weight: 700; min-height: 2.65rem;
    }
    hr { border-color: var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)


SUPPORTED_TYPES = ["sav", "xlsx", "xls", "csv"]
TARGET_N_PER_PHASE = 150
MAX_GITHUB_FILE_BYTES = 50 * 1024 * 1024
PHASE_LABELS = {
    "phase1": "Phase 1 · EFA",
    "phase2": "Phase 2 · CFA & replication",
}


def read_uploaded_data(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    """Read a supported data file without persisting the uploaded file."""
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
    """Convert a public GitHub blob/raw URL to a constrained raw-content URL."""
    parsed = urlsplit(url.strip())
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("Enter a valid HTTPS GitHub file URL.") from error

    host = (parsed.hostname or "").lower()
    if (
        parsed.scheme != "https"
        or host not in {"github.com", "raw.githubusercontent.com"}
        or parsed.username
        or parsed.password
        or port not in (None, 443)
    ):
        raise ValueError(
            "Only public HTTPS GitHub file URLs are supported. Paste a github.com or raw.githubusercontent.com URL."
        )
    if parsed.query or parsed.fragment:
        raise ValueError(
            "Remove query strings and fragments from the URL. Private or tokenized links are not supported."
        )

    path_parts = [part for part in parsed.path.split("/") if part]
    if host == "github.com":
        if (
            len(path_parts) < 5
            or path_parts[2] not in {"blob", "raw"}
            or not all(path_parts[:2])
        ):
            raise ValueError(
                "Use a GitHub file URL in the form github.com/owner/repository/blob/branch/path/file.sav, or paste its raw URL."
            )
        raw_path_parts = path_parts[:2] + path_parts[3:]
    else:
        if len(path_parts) < 4:
            raise ValueError(
                "The raw GitHub URL must include owner, repository, branch, and file path."
            )
        raw_path_parts = path_parts

    file_name = unquote(raw_path_parts[-1])
    if Path(file_name).suffix.lower() not in {f".{kind}" for kind in SUPPORTED_TYPES}:
        raise ValueError("The GitHub file must end in .sav, .xlsx, .xls, or .csv.")

    encoded_path = "/".join(raw_path_parts)
    return f"https://raw.githubusercontent.com/{encoded_path}", file_name


def fetch_public_github_file(url: str) -> tuple[str, bytes]:
    raw_url, file_name = normalize_public_github_url(url)
    try:
        with requests.get(
            raw_url,
            headers={"User-Agent": "AttitudeLab-Psychometrics/1.0"},
            timeout=(5, 20),
            allow_redirects=False,
            stream=True,
        ) as response:
            if 300 <= response.status_code < 400:
                raise ValueError(
                    "GitHub redirected this request. Paste the raw.githubusercontent.com URL instead."
                )
            if response.status_code != 200:
                raise ValueError(
                    f"GitHub returned HTTP {response.status_code}. Confirm the repository and file are public and the link points to a file."
                )

            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_GITHUB_FILE_BYTES:
                raise ValueError("The file exceeds the 50 MB download limit.")

            contents = bytearray()
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                contents.extend(chunk)
                if len(contents) > MAX_GITHUB_FILE_BYTES:
                    raise ValueError("The file exceeds the 50 MB download limit.")
    except requests.RequestException as error:
        raise ValueError(
            "Could not reach the public GitHub file. Check the URL and try again."
        ) from error

    file_bytes = bytes(contents)
    if not file_bytes:
        raise ValueError("The GitHub file is empty.")
    if file_bytes.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError(
            "This URL returned a Git LFS pointer, not the dataset. Use a raw URL that serves the actual file."
        )
    return file_name, file_bytes


def read_github_data(url: str, cache_key: str) -> pd.DataFrame:
    """Load a public GitHub file once per session, then reuse its in-memory bytes."""
    downloads = st.session_state.setdefault("_github_downloads", {})
    cached = downloads.get(cache_key)
    if cached is None or cached["url"] != url.strip():
        file_name, file_bytes = fetch_public_github_file(url)
        cached = {"url": url.strip(), "file_name": file_name, "file_bytes": file_bytes}
        downloads[cache_key] = cached
    return read_uploaded_data(cached["file_name"], cached["file_bytes"])


def numeric_item_columns(data: pd.DataFrame) -> list[str]:
    blocked = ("id", "participant", "respondent", "case", "index", "phase", "group")
    return [
        column
        for column in data.select_dtypes(include="number").columns
        if not any(token in str(column).lower() for token in blocked)
    ]


def as_numeric_items(data: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    return data.loc[:, items].apply(pd.to_numeric, errors="coerce")


def descriptive_table(data: pd.DataFrame, items: list[str]) -> pd.DataFrame:
    numeric = as_numeric_items(data, items)
    records: list[dict[str, Any]] = []
    for item in items:
        values = numeric[item].dropna()
        records.append(
            {
                "Item": item,
                "Valid n": int(values.size),
                "Mean": values.mean() if not values.empty else np.nan,
                "SD": values.std(ddof=1) if values.size > 1 else np.nan,
                "Skewness": values.skew() if values.size > 2 else np.nan,
                "Kurtosis (excess)": values.kurtosis() if values.size > 3 else np.nan,
            }
        )
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
            if values.size > 5000:
                note += "; SciPy cautions that p-values may be inaccurate above n=5,000"
        records.append(
            {
                "Item": item,
                "Valid n": int(values.size),
                "Shapiro–Wilk W": w_value,
                "p-value": p_value,
                "Interpretation": (
                    "Evidence against normality"
                    if pd.notna(p_value) and p_value < 0.05
                    else "No evidence against normality"
                    if pd.notna(p_value)
                    else note
                ),
                "Method note": note,
            }
        )
    return pd.DataFrame(records)


def reliability_result(data: pd.DataFrame, items: list[str]) -> dict[str, Any]:
    numeric = as_numeric_items(data, items)
    complete = numeric.dropna(axis=0, how="any")
    result: dict[str, Any] = {
        "alpha": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "n_complete": int(len(complete)),
        "items": int(len(items)),
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


def efa_result(
    data: pd.DataFrame, items: list[str], factor_count: int, rotation: str
) -> dict[str, Any]:
    numeric = as_numeric_items(data, items)
    complete = numeric.dropna(axis=0, how="any")
    if len(items) < 3:
        raise ValueError("Select at least 3 scale items for exploratory factor analysis.")
    if len(complete) <= len(items):
        raise ValueError(
            f"EFA needs more complete cases than selected items. Current complete-case n={len(complete)} "
            f"and item count={len(items)}."
        )
    constant_items = [
        item for item in items if complete[item].nunique(dropna=True) < 2
    ]
    correlation = None
    if constant_items:
        pass
    try:
        numeric_df = complete.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                # Remove zero-variance columns to prevent division by zero
                numeric_df = numeric_df.loc[:, numeric_df.std(ddof=0) > 0]
                # Calculate correlation and replace any remaining NaNs with 0
                correlation = numeric_df.corr().fillna(0)
        except Exception as e:
            pass

   # if correlation is None or correlation.empty or not np.isfinite(correlation.to_numpy()).all():
   #     raise ValueError("The item correlation matrix contains undefined or missing numeric values.")
    # Import necessary libraries
    from factor_analyzer import FactorAnalyzer
    from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
    import pandas as pd
    import numpy as np

    # 1. Calculate KMO and Bartlett's test
    try:
        kmo_all, kmo_model = calculate_kmo(complete)
        bartlett_chi2, bartlett_p = calculate_bartlett_sphericity(complete)
    except Exception:
        kmo_all = np.full(len(items), np.nan)
        kmo_model = np.nan
        bartlett_chi2 = np.nan
        bartlett_p = np.nan

    kmo_items = pd.Series(kmo_all, index=items)

    # 2. Fit EFA using Principal Component Analysis (PCA) to match SPSS
    fa = FactorAnalyzer(n_factors=factor_count, rotation=rotation, method='principal')
    fa.fit(complete)

    # 3. Extract factor loadings
    loadings = pd.DataFrame(fa.loadings_, index=items, columns=[f"Factor {i+1}" for i in range(factor_count)])

    # 4. Extract eigenvalues
    ev, _ = fa.get_eigenvalues()
    eigenvalues_df = pd.DataFrame({
        "Component": range(1, len(ev) + 1),
        "Eigenvalue": ev
    })

    # 5. Return the results dictionary
    return {
        "n_complete": len(complete),
        "kmo": kmo_model,
        "kmo_items": kmo_items,
        "bartlett_chi2": bartlett_chi2,
        "bartlett_p": bartlett_p,
        "method": "PCA (Principal Component Analysis)",
        "rotation": rotation,
        "factor_count": factor_count,
        "loadings": loadings,
        "eigenvalues": eigenvalues_df
    }    
             

def build_cfa_specification(
    factor_assignments: dict[str, list[str]],
) -> dict[str, Any]:
    used_items = [
        item
        for factor_items in factor_assignments.values()
        for item in factor_items
    ]
    if not used_items:
        raise ValueError("Assign at least three items to a CFA factor.")
    if len(used_items) != len(set(used_items)):
        raise ValueError(
            "Each item can be assigned to only one factor in this simple-structure model."
        )
    for factor, factor_items in factor_assignments.items():
        if factor_items and len(factor_items) < 3:
            raise ValueError(
                f"{factor} has {len(factor_items)} item(s). Assign at least three indicators to each factor."
            )
    if any(not factor_items for factor_items in factor_assignments.values()):
        raise ValueError("Remove empty factors or assign items to each factor.")

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
        semopy_lines.append(
            f"{factor_alias} =~ " + " + ".join(aliases[item] for item in factor_items)
        )
        display_lines.append(f"{factor} =~ " + " + ".join(map(str, factor_items)))

    return {
        "items": used_items,
        "aliases": aliases,
        "alias_to_item": alias_to_item,
        "factor_aliases": factor_aliases,
        "engine_syntax": "\n".join(semopy_lines),
        "display_syntax": "\n".join(display_lines),
    }


def cfa_result(
    data: pd.DataFrame,
    factor_assignments: dict[str, list[str]],
    specification: dict[str, Any],
) -> dict[str, Any]:
    items = specification["items"]
    complete = as_numeric_items(data, items).dropna(axis=0, how="any")
    if len(complete) <= len(items):
        raise ValueError(
            f"CFA needs more complete cases than modeled items. Current complete-case n={len(complete)} and item count={len(items)}."
        )
    constant_items = [item for item in items if complete[item].nunique() < 2]
    if constant_items:
        raise ValueError(
            "These modeled items have no variability among complete cases: "
            + ", ".join(map(str, constant_items))
        )
    renamed = complete.rename(columns=specification["aliases"])
    model = Model(specification["engine_syntax"])
    fit_result = model.fit(renamed, obj="MLW")
    if not fit_result.success:
        raise ValueError(
            f"The CFA optimizer did not converge: {fit_result.message or 'no convergence details returned'}"
        )

    fit_table = calc_stats(model).iloc[0]
    fit_names = [
        "chi2",
        "DoF",
        "chi2 p-value",
        "CFI",
        "TLI",
        "RMSEA",
        "AIC",
        "BIC",
        "LogLik",
    ]
    fit_values: dict[str, float] = {}
    for name in fit_names:
        value = fit_table.get(name, np.nan)
        fit_values[name] = float(value) if pd.notna(value) else np.nan

    parameters = model.inspect(std_est=True)
    for column in ("Estimate", "Est. Std", "Std. Err", "z-value", "p-value"):
        if column in parameters.columns:
            parameters[column] = pd.to_numeric(parameters[column], errors="coerce")
    for column in ("lval", "rval"):
        parameters[column] = parameters[column].replace(
            {
                **specification["alias_to_item"],
                **specification["factor_aliases"],
            }
        )
    parameters = parameters.rename(
        columns={
            "lval": "Left",
            "op": "Operator",
            "rval": "Right",
            "Estimate": "Estimate",
            "Est. Std": "Standardized estimate",
            "Std. Err": "SE",
            "z-value": "z",
            "p-value": "p",
        }
    )

    return {
        "n_complete": int(len(complete)),
        "item_count": len(items),
        "factor_count": len(factor_assignments),
        "fit": fit_values,
        "parameters": parameters,
        "specification": specification,
        "estimator": "Maximum likelihood (MLW)",
        "assumption": "Selected item responses are treated as approximately continuous.",
    }


def add_report_rows(
    report_rows: list[dict[str, Any]],
    phase: str,
    metric: str,
    variable: str,
    value: Any,
    n_used: Any = "",
    notes: str = "",
) -> None:
    report_rows.append(
        {
            "Phase": phase,
            "Metric": metric,
            "Variable": variable,
            "Value": value,
            "n used": n_used,
            "Notes": notes,
        }
    )


def add_phase_report(
    report_rows: list[dict[str, Any]],
    phase: str,
    data: pd.DataFrame,
    items: list[str],
    descriptives: pd.DataFrame,
    normality: pd.DataFrame,
    reliability: dict[str, Any],
) -> None:
    add_report_rows(
        report_rows,
        phase,
        "Sample size",
        "Rows in uploaded phase",
        int(len(data)),
        int(len(data)),
        f"Target n={TARGET_N_PER_PHASE}; check actual value against study plan.",
    )
    for _, row in descriptives.iterrows():
        for metric in ("Valid n", "Mean", "SD", "Skewness", "Kurtosis (excess)"):
            add_report_rows(
                report_rows,
                phase,
                metric,
                str(row["Item"]),
                row[metric],
                row["Valid n"],
                "Kurtosis is reported as excess kurtosis (normal distribution = 0).",
            )
    for _, row in normality.iterrows():
        for metric in ("Shapiro–Wilk W", "p-value"):
            add_report_rows(
                report_rows,
                phase,
                metric,
                str(row["Item"]),
                row[metric],
                row["Valid n"],
                str(row["Method note"]),
            )
    for metric, value in (
        ("Cronbach's alpha", reliability["alpha"]),
        ("Alpha CI lower", reliability["ci_low"]),
        ("Alpha CI upper", reliability["ci_high"]),
    ):
        add_report_rows(
            report_rows,
            phase,
            metric,
            "Selected scale items",
            value,
            reliability["n_complete"],
            reliability["note"],
        )


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
        st.warning(
            f"{PHASE_LABELS[phase_key]} contains {n} rows; the study plan specifies "
            f"{TARGET_N_PER_PHASE}. Results use the uploaded data as-is."
        )


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Open science · Psychometrics</div>
      <h1 style="margin:0">Attitude Lab</h1>
      <p>Explore the measurement quality of employee attitudes toward generative AI, with transparent samples, methods, and exportable results.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("### Study workspace")
    st.caption("Employee Attitudes toward Generative AI")
    st.markdown("---")
    source_mode = st.radio(
        "How is your data organized?",
        ["Two phase files", "One combined file"],
        help="Use two uploads when each phase is in a separate file, or a combined file with one column identifying the phase.",
    )
    data_source = st.radio(
    "Where are the files?",
    ["Upload from device", "Public GitHub URLs"],
    index=1,
    help="GitHub inputs support public HTTPS file links only. Private repositories and tokenized links are not supported.",
   )
    st.markdown("#### Study data")
try:
    with open("demo_phase1.sav", "rb") as f1:
        phase1_data = read_uploaded_data("demo_phase1.sav", f1.read())
    with open("demo_phase2.sav", "rb") as f2:
        phase2_data = read_uploaded_data("demo_phase2.sav", f2.read())
except Exception as e:
    pass
        
if source_mode == "Two phase files":
    
    if data_source == "Upload from device":
        phase1_file = st.file_uploader(
            "Phase 1 - EFA sample",
            type=SUPPORTED_TYPES,
            key="phase1_upload",
            help="Planned sample: 150 cases. Supported: SPSS, Excel, CSV."
        )
        phase2_file = st.file_uploader(
            "Phase 2 - CFA sample",
            type=SUPPORTED_TYPES,
            key="phase2_upload",
            help="Planned sample: 150 cases. Supported: SPSS, Excel, CSV."
        )
        for uploaded, label in ((phase1_file, "Phase 1"), (phase2_file, "Phase 2")):
            if uploaded is not None:
                try:
                    loaded = read_uploaded_data(uploaded.name, uploaded.getvalue())
                    if label == "Phase 1":
                        phase1_data = loaded
                    else:
                        phase2_data = loaded
                except Exception as error:
                    st.error(f"Could not read the {label} file: {error}")
    else:
        st.caption("Paste public GitHub blob or raw file URLs. Private repositories, query strings, and files over 50 MB are not supported.")
        phase1_url = st.text_input("Phase 1 - GitHub file URL", placeholder="https://github.com", key="phase1_github_url")
        phase2_url = st.text_input("Phase 2 - GitHub file URL", placeholder="https://github.com/owner/repo/blob/main/phase2.sav", key="phase2_github_url")
        for url, label, cache_key in ((phase1_url, "Phase 1", "phase1"), (phase2_url, "Phase 2", "phase2")):
            if url.strip():
                try:
                    with st.spinner(f"Fetching the public {label} file from GitHub..."):
                        loaded = read_github_data(url, cache_key)
                        if label == "Phase 1":
                            phase1_data = loaded
                        else:
                            phase2_data = loaded
                except Exception as error:
                    st.error(f"Could not load the {label} GitHub file: {error}")
                    

                if phase1_value == phase2_value:
                    st.error("Choose two different values for the study phases.")
                else:
                    phase1_data = combined_data.loc[
                        combined_data[phase_column] == phase1_value
                    ].drop(columns=[phase_column])
                    phase2_data = combined_data.loc[
                        combined_data[phase_column] == phase2_value
                    ].drop(columns=[phase_column])

    if phase1_data is not None or phase2_data is not None:
        st.markdown("---")
        st.caption("Privacy & data handling")
        st.caption(
            "Files are processed in server-side app memory for this session and are not intentionally written to a project database. "
            "GitHub fetching is restricted to public GitHub file hosts. Use de-identified data and avoid direct identifiers."
        )


if phase1_data is None and phase2_data is None:
    st.markdown(
        """
        <div class="section-card">
          <h3 style="margin:0">Start with your study data</h3>
          <p>Upload the phase files or paste public GitHub links. Use Phase 1 for EFA and Phase 2 for CFA validation, replication descriptives, normality checks, and reliability.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    intro_cols = st.columns(3)
    with intro_cols[0]:
        st.markdown("#### 01 · Explore")
        st.markdown("Estimate factorability and an exploratory factor solution from Phase 1.")
    with intro_cols[1]:
        st.markdown("#### 02 · Describe")
        st.markdown("Review distributions, normality tests, and reliability for each phase.")
    with intro_cols[2]:
        st.markdown("#### 03 · Share")
        st.markdown("Export results as a tidy CSV with methods and sample-size notes.")
    st.info(
        "The planned design is 150 cases per phase (total N = 300). The app reports actual uploaded sample sizes and never creates or imputes study data."
    )
    st.stop()

selected_items = []
available_data = [data for data in (phase1_data, phase2_data) if data is not None]
common_columns = set(available_data[0].columns) if available_data else set()
for data in available_data[1:]:
    common_columns &= set(data.columns)

numeric_items = []
if available_data:
    excluded_keywords = ['id', 'participant', 'case', 'total', 'gender', 'sex', 'الجنس', 'المجموع']
    numeric_items = [col for col in available_data[0].select_dtypes(include=[np.number]).columns if col in common_columns and not any(kw in str(col).lower() for kw in excluded_keywords)]

if not numeric_items:
    st.error("No shared numeric item columns were found across the phase files.")
    st.stop()

with st.expander("Review uploaded data before selecting items"):
    if phase1_data is not None:
        st.caption(f"Phase 1 · {len(phase1_data)} rows extracted")
        st.dataframe(phase1_data.head(6), use_container_width=True)
    if phase2_data is not None:
        st.caption(f"Phase 2 · {len(phase2_data)} rows extracted")
        st.dataframe(phase2_data.head(6), use_container_width=True)

st.markdown("### Select scale items")
st.caption("Explicitly choose only the response items belonging to your psychometric scale.")

default_items = [col for col in numeric_items if str(col).lower().startswith('s') and str(col).lower() not in ["some", "some1", "some2"]]
if not default_items and numeric_items:
    default_items = numeric_items[:min(10, len(numeric_items))]

selected_items = st.multiselect("Scale item columns", options=numeric_items, default=default_items, format_func=str)


if not selected_items:
    st.warning(
        "Select the scale response columns to continue. No analysis runs until you choose them."
    )
    st.stop()


tabs = st.tabs(
    ["Study overview", "Phase 1 · EFA", "Phase 2 · CFA & replication", "Open report"]
)
report_rows: list[dict[str, Any]] = []
efa_output: dict[str, Any] | None = None
phase1_descriptives: pd.DataFrame | None = None
phase1_normality: pd.DataFrame | None = None
phase1_reliability: dict[str, Any] | None = None
phase2_descriptives: pd.DataFrame | None = None
phase2_normality: pd.DataFrame | None = None
phase2_reliability: dict[str, Any] | None = None
cfa_output: dict[str, Any] | None = None
cfa_error: str | None = None


with tabs[0]:
    st.markdown("### Study overview")
    phase_cols = st.columns(3)
    phase_cols[0].metric(
        "Total uploaded cases",
        sum(len(data) for data in (phase1_data, phase2_data) if data is not None),
        help="Sum of the uploaded phase samples. Missing or excluded responses are handled per analysis.",
    )
    phase_cols[1].metric(
        "Phase 1 cases",
        len(phase1_data) if phase1_data is not None else "Not uploaded",
        delta=(
            f"Target {TARGET_N_PER_PHASE}"
            if phase1_data is not None and len(phase1_data) == TARGET_N_PER_PHASE
            else None
        ),
    )
    phase_cols[2].metric(
        "Phase 2 cases",
        len(phase2_data) if phase2_data is not None else "Not uploaded",
        delta=(
            f"Target {TARGET_N_PER_PHASE}"
            if phase2_data is not None and len(phase2_data) == TARGET_N_PER_PHASE
            else None
        ),
    )
    st.markdown(
        """
        <div class="section-card">
          <span class="pill">Open methods</span><span class="pill">Transparent missing-data handling</span>
          <p>Descriptive statistics use available item responses. Reliability, EFA, and CFA use listwise-complete rows across the items included in each analysis; each result reports its valid n. No cases are synthesized.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if phase1_data is not None:
        show_sample_note(phase1_data, "phase1")
    if phase2_data is not None:
        show_sample_note(phase2_data, "phase2")
    st.caption(
        "Phase 2 can test a theory-led measurement model specified by the researcher. Phase 1 EFA loadings can suggest starting item assignments, which you can review before fitting."
    )


with tabs[1]:
    st.markdown("### Exploratory factor analysis")
    st.caption(
        "Phase 1 is the designated discovery sample. EFA is fitted to listwise-complete responses for the selected items."
    )
    if phase1_data is None:
        st.info("Upload a Phase 1 file in the sidebar to explore the factor structure.")
    else:
        show_sample_note(phase1_data, "phase1")
        phase1_descriptives = descriptive_table(phase1_data, selected_items)
        phase1_normality = normality_table(phase1_data, selected_items)
        phase1_reliability = reliability_result(phase1_data, selected_items)
        add_phase_report(
            report_rows,
            PHASE_LABELS["phase1"],
            phase1_data,
            selected_items,
            phase1_descriptives,
            phase1_normality,
            phase1_reliability,
        )
        try:
            complete = as_numeric_items(phase1_data, selected_items).dropna()
            if len(selected_items) < 3:
                raise ValueError("Select at least 3 scale items for exploratory factor analysis.")
            if len(complete) <= len(selected_items):
                raise ValueError(
                    f"Current complete-case n={len(complete)} is not greater than the number of items ({len(selected_items)})."
                )
            if any(complete[item].nunique() < 2 for item in selected_items):
                constant = [
                    item for item in selected_items if complete[item].nunique() < 2
                ]
                raise ValueError(
                    "Items with no variability must be corrected or removed: "
                    + ", ".join(map(str, constant))
                )
            eigenvalues = np.linalg.eigvalsh(complete.corr().to_numpy())[::-1]
            suggested_factors = int((eigenvalues > 1).sum())
            max_factors = max(1, len(selected_items) - 1)
            recommended = min(max(1, suggested_factors), max_factors)
            controls = st.columns(2)
            with controls[0]:
                factor_count = st.number_input(
                    "Factors to retain",
                    min_value=1,
                    max_value=max_factors,
                    value=recommended,
                    step=1,
                    help=f"Kaiser criterion suggests {suggested_factors} component(s) with eigenvalue > 1. Use theory and the scree plot as well; this is a heuristic, not a retention rule.",
                )
            with controls[1]:
                rotation = st.selectbox(
                    "Rotation",
                    ["oblimin", "varimax"],
                    help="Oblimin allows factors to correlate; varimax constrains factor correlations to zero.",
                )
            efa_output = efa_result(
                phase1_data,
                selected_items,
                int(factor_count),
                rotation,
            )
            
            metrics[2].metric(
                "Bartlett χ²",
                f"{efa_output['bartlett_chi2']:.2f}",
            ) 
            metrics[3].metric("Bartlett p", f"{efa_output['bartlett_p']:.4g}")
            st.markdown("#### Eigenvalues")
            st.dataframe(
                efa_output["eigenvalues"].style.format({"Eigenvalue": "{:.3f}"}),
                width="stretch",
                hide_index=True,
            )
            st.markdown("#### Factor loadings")
            st.caption(
                f"{efa_output['method']} extraction · {efa_output['rotation']} rotation · "
                f"{efa_output['factor_count']} factor(s). Loadings are pattern coefficients."
            )
            st.dataframe(
                efa_output["loadings"].style.format("{:.3f}"),
                width="stretch",
            )
            st.markdown("#### Item-level KMO")
            st.dataframe(
                efa_output["kmo_items"].rename_axis("Item").reset_index().style.format(
                    {"KMO": "{:.3f}"}
                ),
                width="stretch",
                hide_index=True,
            )
            st.caption(
                "KMO and Bartlett's test assess whether the correlation matrix is suitable for factor analysis; neither establishes that the extracted solution is valid. Review item content, residuals, factor retention, and sample adequacy."
            )
            for _, row in efa_output["eigenvalues"].iterrows():
                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase1"],
                    "Correlation-matrix eigenvalue",
                    row["Component"],
                    row["Eigenvalue"],
                    efa_output["n_complete"],
                    "Kaiser > 1 shown as a heuristic only.",
                )
            add_report_rows(
                report_rows,
                PHASE_LABELS["phase1"],
                "Overall KMO",
                "Selected scale items",
                efa_output["kmo"],
                efa_output["n_complete"],
                "Kaiser-Meyer-Olkin measure of sampling adequacy.",
            )
            add_report_rows(
                report_rows,
                PHASE_LABELS["phase1"],
                "Bartlett's test chi-square",
                "Correlation matrix",
                efa_output["bartlett_chi2"],
                efa_output["n_complete"],
                "Bartlett test of sphericity.",
            )
            add_report_rows(
                report_rows,
                PHASE_LABELS["phase1"],
                "Bartlett's test p-value",
                "Correlation matrix",
                efa_output["bartlett_p"],
                efa_output["n_complete"],
                "Bartlett test of sphericity.",
            )
            for metric, value, note in (
                ("EFA factor count", efa_output["factor_count"], "User-selected factor count."),
                ("EFA extraction", efa_output["method"], "Exploratory factor model."),
                ("EFA rotation", efa_output["rotation"], "User-selected rotation."),
            ):
                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase1"],
                    metric,
                    "Factor model",
                    value,
                    efa_output["n_complete"],
                    note,
                )
            for item, value in efa_output["kmo_items"].items():
                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase1"],
                    "Item-level KMO",
                    str(item),
                    value,
                    efa_output["n_complete"],
                    "Kaiser-Meyer-Olkin measure of sampling adequacy.",
                )
            for item, loading_row in efa_output["loadings"].iterrows():
                for factor, loading in loading_row.items():
                    add_report_rows(
                        report_rows,
                        PHASE_LABELS["phase1"],
                        "Factor loading",
                        f"{item} · {factor}",
                        loading,
                        efa_output["n_complete"],
                        f"{efa_output['method']}; {efa_output['rotation']} rotation.",
                    )
        except Exception as error:
            st.error(f"EFA could not be completed: {error}")
            add_report_rows(
                report_rows,
                PHASE_LABELS["phase1"],
                "EFA status",
                "Factor model",
                "Not computed",
                "",
                str(error),
            )

        st.markdown("#### Phase 1 descriptive statistics")
        st.dataframe(
            phase1_descriptives.style.format(
                {
                    "Mean": "{:.3f}",
                    "SD": "{:.3f}",
                    "Skewness": "{:.3f}",
                    "Kurtosis (excess)": "{:.3f}",
                }
            ),
            width="stretch",
            hide_index=True,
        )
        st.markdown("#### Phase 1 normality checks")
        st.dataframe(
            phase1_normality.style.format(
                {"Shapiro–Wilk W": "{:.4f}", "p-value": "{:.4g}"}
            ),
            width="stretch",
            hide_index=True,
        )
        phase1_plot_item = st.selectbox(
            "Inspect a Phase 1 item distribution",
            options=selected_items,
            key="phase1_plot_item",
        )
        render_distribution(
            phase1_data,
            phase1_plot_item,
            PHASE_LABELS["phase1"],
        )
        st.markdown("#### Phase 1 reliability")
        if pd.notna(phase1_reliability["alpha"]):
            st.metric(
                "Cronbach's alpha",
                f"{phase1_reliability['alpha']:.3f}",
                help="Listwise-complete cases across the selected items.",
            )
            st.caption(
                f"95% CI [{phase1_reliability['ci_low']:.3f}, "
                f"{phase1_reliability['ci_high']:.3f}] · "
                f"{phase1_reliability['note']}"
            )
        else:
            st.warning(phase1_reliability["note"])


with tabs[2]:
    st.markdown("### Phase 2 confirmatory factor analysis")
    st.caption(
        "Fit the reviewed measurement structure on the independent Phase 2 sample. EFA-based assignments are suggestions only; confirm them against theory before fitting."
    )
    if phase2_data is None:
        st.info("Upload a Phase 2 file in the sidebar to review the replication sample.")
    else:
        show_sample_note(phase2_data, "phase2")
        phase2_descriptives = descriptive_table(phase2_data, selected_items)
        phase2_normality = normality_table(phase2_data, selected_items)
        phase2_reliability = reliability_result(phase2_data, selected_items)
        add_phase_report(
            report_rows,
            PHASE_LABELS["phase2"],
            phase2_data,
            selected_items,
            phase2_descriptives,
            phase2_normality,
            phase2_reliability,
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric("Scale items", len(selected_items))
        metric_cols[1].metric(
            "Complete cases for alpha",
            phase2_reliability["n_complete"],
        )
        metric_cols[2].metric(
            "Cronbach's alpha",
            (
                f"{phase2_reliability['alpha']:.3f}"
                if pd.notna(phase2_reliability["alpha"])
                else "Unavailable"
            ),
            help="Listwise-complete cases across the selected items.",
        )
        if pd.notna(phase2_reliability["alpha"]):
            st.caption(
                f"95% CI [{phase2_reliability['ci_low']:.3f}, {phase2_reliability['ci_high']:.3f}] · "
                f"{phase2_reliability['note']}"
            )
        else:
            st.warning(phase2_reliability["note"])
        st.markdown("#### Descriptive statistics")
        st.dataframe(
            phase2_descriptives.style.format(
                {
                    "Mean": "{:.3f}",
                    "SD": "{:.3f}",
                    "Skewness": "{:.3f}",
                    "Kurtosis (excess)": "{:.3f}",
                }
            ),
            width="stretch",
            hide_index=True,
        )
        st.markdown("#### Normality checks")
        st.dataframe(
            phase2_normality.style.format(
                {"Shapiro–Wilk W": "{:.4f}", "p-value": "{:.4g}"}
            ),
            width="stretch",
            hide_index=True,
        )
        plot_item = st.selectbox(
            "Inspect item distribution",
            options=selected_items,
            key="phase2_plot_item",
        )
        render_distribution(
            phase2_data,
            plot_item,
            PHASE_LABELS["phase2"],
        )

        st.markdown("---")
        st.markdown("### Specify the Phase 2 measurement model")
        st.caption(
            "Each item is assigned to one factor in this simple-structure CFA. Factors may correlate; the app does not add cross-loadings or correlated residuals."
        )
        if efa_output is not None:
            st.info(
                "Starting assignments are suggested from each item's strongest absolute Phase 1 EFA loading. Review or change them based on theory before fitting."
            )
        else:
            st.info(
                "No usable Phase 1 EFA solution is available. A one-factor draft is shown; edit it to match your theory-driven model."
            )

        max_cfa_factors = max(1, min(6, len(selected_items) // 3))
        suggested_cfa_factors = (
            min(max(1, int(efa_output["factor_count"])), max_cfa_factors)
            if efa_output is not None
            else 1
        )
        cfa_items_key = hashlib.sha1(
            "|".join(map(str, selected_items)).encode("utf-8")
        ).hexdigest()[:10]
        cfa_factor_count = int(
            st.number_input(
                "Number of CFA factors",
                min_value=1,
                max_value=max_cfa_factors,
                value=suggested_cfa_factors,
                step=1,
                key=f"cfa_factor_count_{cfa_items_key}",
                help="A maximum of six factors is shown. Each factor needs at least three indicators in this guided model builder.",
            )
        )
        cfa_factor_labels = [
            f"Factor {index + 1}" for index in range(cfa_factor_count)
        ]
        default_assignment_by_item = {
            item: (cfa_factor_labels[0] if not efa_output else "Not included")
            for item in selected_items
        }
        if efa_output is not None:
            efa_loadings = efa_output["loadings"]
            for item in selected_items:
                if item not in efa_loadings.index:
                    continue
                item_loadings = efa_loadings.loc[item]
                strongest_factor = item_loadings.abs().idxmax()
                if (
                    strongest_factor in cfa_factor_labels
                    and abs(float(item_loadings[strongest_factor])) >= 0.30
                ):
                    default_assignment_by_item[item] = strongest_factor

        st.markdown("#### Assign items to factors")
        assignment_columns = st.columns(2)
        assignment_by_item: dict[str, str] = {}
        select_options = ["Not included", *cfa_factor_labels]
        for item_index, item in enumerate(selected_items):
            default_assignment = default_assignment_by_item[item]
            if default_assignment not in select_options:
                default_assignment = "Not included"
            with assignment_columns[item_index % 2]:
                assignment_by_item[item] = st.selectbox(
                    str(item),
                    options=select_options,
                    index=select_options.index(default_assignment),
                    key=(
                        "cfa_assignment_"
                        + hashlib.sha1(str(item).encode("utf-8")).hexdigest()[:10]
                        + f"_{cfa_factor_count}"
                    ),
                )

        factor_assignments = {
            factor: [
                item
                for item, assigned_factor in assignment_by_item.items()
                if assigned_factor == factor
            ]
            for factor in cfa_factor_labels
        }
        cfa_specification = None
        cfa_validation_error = None
        try:
            cfa_specification = build_cfa_specification(factor_assignments)
        except ValueError as error:
            cfa_validation_error = str(error)

        if cfa_validation_error:
            st.warning(cfa_validation_error)
        if len(selected_items) < 3:
            cfa_validation_error = (
                "Select at least three scale items before fitting a CFA."
            )
            st.warning(cfa_validation_error)

        if cfa_specification is not None:
            st.markdown("#### Model specification")
            st.code(cfa_specification["display_syntax"], language="text")
            with st.expander("Analysis column aliases"):
                alias_table = pd.DataFrame(
                    [
                        {"Original item": item, "Analysis column": alias}
                        for item, alias in cfa_specification["aliases"].items()
                    ]
                )
                st.dataframe(alias_table, width="stretch", hide_index=True)
            st.caption(
                "Estimator: maximum likelihood (MLW). Selected responses are treated as approximately continuous. Missing values are handled by listwise deletion for the items included in this model."
            )

            cfa_complete_for_signature = as_numeric_items(
                phase2_data, cfa_specification["items"]
            ).dropna(axis=0, how="any")
            cfa_data_digest = hashlib.sha256(
                pd.util.hash_pandas_object(
                    cfa_complete_for_signature, index=True
                ).values.tobytes()
            ).hexdigest()
            cfa_signature = hashlib.sha256(
                (
                    cfa_data_digest
                    + cfa_specification["engine_syntax"]
                    + "MLW"
                ).encode("utf-8")
            ).hexdigest()
            fit_cfa = st.button(
                "Fit Phase 2 CFA",
                type="primary",
                key="fit_phase2_cfa",
                disabled=bool(cfa_validation_error),
            )
            if fit_cfa:
                try:
                    with st.spinner("Fitting the Phase 2 CFA model…"):
                        fitted_cfa = cfa_result(
                            phase2_data,
                            factor_assignments,
                            cfa_specification,
                        )
                    st.session_state["_cfa_fit_result"] = {
                        "signature": cfa_signature,
                        "result": fitted_cfa,
                        "error": None,
                    }
                except Exception as error:
                    st.session_state["_cfa_fit_result"] = {
                        "signature": cfa_signature,
                        "result": None,
                        "error": str(error),
                    }

            cached_cfa = st.session_state.get("_cfa_fit_result")
            if cached_cfa and cached_cfa["signature"] == cfa_signature:
                cfa_output = cached_cfa["result"]
                cfa_error = cached_cfa["error"]

            if cfa_error:
                st.error(f"CFA could not be completed: {cfa_error}")
            elif cfa_output is None:
                st.info("Review the proposed item assignments, then fit the model.")
            else:
                if cfa_output["fit"]["DoF"] <= 0:
                    st.warning(
                        "This model has zero or negative degrees of freedom, so global fit indices are not informative."
                    )
                st.markdown("#### Model fit")

                def cfa_metric(value: float, digits: int = 3) -> str:
                    return f"{value:.{digits}f}" if np.isfinite(value) else "—"

                fit_values = cfa_output["fit"]
                fit_metrics = st.columns(4)
                fit_metrics[0].metric("CFI", cfa_metric(fit_values["CFI"]))
                fit_metrics[1].metric("TLI", cfa_metric(fit_values["TLI"]))
                fit_metrics[2].metric("RMSEA", cfa_metric(fit_values["RMSEA"]))
                fit_metrics[3].metric(
                    "χ² (df)",
                    f"{cfa_metric(fit_values['chi2'], 2)} "
                    f"({cfa_metric(fit_values['DoF'], 0)})",
                )
                fit_metrics[0].caption(f"Phase 2 complete n = {cfa_output['n_complete']}")
                fit_table = pd.DataFrame(
                    [
                        {"Fit statistic": label, "Value": value}
                        for label, value in (
                            ("Chi-square", fit_values["chi2"]),
                            ("Degrees of freedom", fit_values["DoF"]),
                            ("Chi-square p-value", fit_values["chi2 p-value"]),
                            ("CFI", fit_values["CFI"]),
                            ("TLI", fit_values["TLI"]),
                            ("RMSEA", fit_values["RMSEA"]),
                            ("AIC", fit_values["AIC"]),
                            ("BIC", fit_values["BIC"]),
                            ("Log likelihood", fit_values["LogLik"]),
                        )
                    ]
                )
                st.dataframe(
                    fit_table.style.format({"Value": "{:.4f}", "Fit statistic": "{}"}),
                    width="stretch",
                    hide_index=True,
                )
                st.markdown("#### Parameter estimates")
                st.dataframe(
                    cfa_output["parameters"].style.format(
                        {
                            "Estimate": "{:.3f}",
                            "Standardized estimate": "{:.3f}",
                            "SE": "{:.3f}",
                            "z": "{:.3f}",
                            "p": "{:.4g}",
                        },
                        na_rep="—",
                    ),
                    width="stretch",
                    hide_index=True,
                )
                st.caption(
                    "Fit indices do not have universal pass/fail cutoffs. Interpret model fit, parameter estimates, confidence intervals, residuals, and theory together; report the estimator and item treatment explicitly."
                )

                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase2"],
                    "CFA status",
                    "Measurement model",
                    "Converged",
                    cfa_output["n_complete"],
                    cfa_output["estimator"],
                )
                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase2"],
                    "CFA model syntax",
                    "Measurement model",
                    cfa_specification["display_syntax"],
                    cfa_output["n_complete"],
                    "Simple-structure model; no cross-loadings or correlated residuals.",
                )
                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase2"],
                    "CFA executable syntax",
                    "semopy model",
                    cfa_specification["engine_syntax"],
                    cfa_output["n_complete"],
                    "Uses the analysis aliases listed in the CFA item alias rows.",
                )
                add_report_rows(
                    report_rows,
                    PHASE_LABELS["phase2"],
                    "CFA estimator",
                    "Measurement model",
                    cfa_output["estimator"],
                    cfa_output["n_complete"],
                    cfa_output["assumption"],
                )
                for metric_name, metric_value in fit_values.items():
                    add_report_rows(
                        report_rows,
                        PHASE_LABELS["phase2"],
                        f"CFA {metric_name}",
                        "Measurement model",
                        metric_value,
                        cfa_output["n_complete"],
                        cfa_output["assumption"],
                    )
                for item, alias in cfa_specification["aliases"].items():
                    add_report_rows(
                        report_rows,
                        PHASE_LABELS["phase2"],
                        "CFA item alias",
                        str(item),
                        alias,
                        cfa_output["n_complete"],
                        "Maps the original data column to the model syntax identifier.",
                    )
                for _, parameter in cfa_output["parameters"].iterrows():
                    parameter_name = (
                        f"{parameter['Left']} {parameter['Operator']} {parameter['Right']}"
                    )
                    for estimate_name in (
                        "Estimate",
                        "Standardized estimate",
                        "SE",
                        "z",
                        "p",
                    ):
                        add_report_rows(
                            report_rows,
                            PHASE_LABELS["phase2"],
                            f"CFA parameter {estimate_name}",
                            parameter_name,
                            parameter[estimate_name],
                            cfa_output["n_complete"],
                            cfa_output["estimator"],
                        )
        elif cfa_error:
            st.error(f"CFA could not be completed: {cfa_error}")


with tabs[3]:
    st.markdown("### Open analysis report")
    st.caption(
        "A tidy, machine-readable CSV containing descriptive, reliability, EFA, and CFA results, analysis sample sizes, and method notes."
    )
    if phase1_data is not None and phase1_descriptives is None:
        phase1_descriptives = descriptive_table(phase1_data, selected_items)
        phase1_normality = normality_table(phase1_data, selected_items)
        phase1_reliability = reliability_result(phase1_data, selected_items)
        add_phase_report(
            report_rows,
            PHASE_LABELS["phase1"],
            phase1_data,
            selected_items,
            phase1_descriptives,
            phase1_normality,
            phase1_reliability,
        )
    if phase2_data is not None and phase2_descriptives is None:
        phase2_descriptives = descriptive_table(phase2_data, selected_items)
        phase2_normality = normality_table(phase2_data, selected_items)
        phase2_reliability = reliability_result(phase2_data, selected_items)
        add_phase_report(
            report_rows,
            PHASE_LABELS["phase2"],
            phase2_data,
            selected_items,
            phase2_descriptives,
            phase2_normality,
            phase2_reliability,
        )
    add_report_rows(
        report_rows,
        "Study",
        "Total uploaded cases",
        "Both phases",
        sum(len(data) for data in (phase1_data, phase2_data) if data is not None),
        sum(len(data) for data in (phase1_data, phase2_data) if data is not None),
        "Planned design: 150 Phase 1 + 150 Phase 2 cases (total N=300).",
    )
    add_report_rows(
        report_rows,
        "Study",
        "Scale",
        "Instrument",
        "Employee Attitudes toward Generative AI",
        "",
        f"Selected items: {', '.join(map(str, selected_items))}",
    )
    if phase2_data is None:
        add_report_rows(
            report_rows,
            PHASE_LABELS["phase2"],
            "CFA status",
            "Measurement model",
            "Not available",
            "",
            "Upload a Phase 2 sample to fit a confirmatory factor analysis.",
        )
    elif cfa_output is None:
        add_report_rows(
            report_rows,
            PHASE_LABELS["phase2"],
            "CFA status",
            "Measurement model",
            "Not fitted" if cfa_error is None else "Not converged",
            "",
            (
                "Specify and fit the measurement model in the Phase 2 tab."
                if cfa_error is None
                else cfa_error
            ),
        )
    if efa_output is not None:
        # EFA rows are added in the Phase 1 tab above.
        pass
    else:
        add_report_rows(
            report_rows,
            PHASE_LABELS["phase1"],
            "EFA status",
            "Factor model",
            "Not available",
            "",
            "EFA requires a Phase 1 sample, at least 3 selected items, and a valid item correlation matrix.",
        )
    report = pd.DataFrame(report_rows)
    if not report.empty:
        report_view = report.copy()
        for column in ("Value", "n used"):
            if column in report_view:
                report_view[column] = report_view[column].map(
                    lambda value: "" if pd.isna(value) else str(value)
                )
        st.dataframe(report_view, width="stretch", hide_index=True)
        st.download_button(
            "Download analysis report · CSV",
            data=report.to_csv(index=False).encode("utf-8-sig"),
            file_name="employee_ai_attitudes_psychometric_report.csv",
            mime="text/csv",
            type="primary",
        )
    else:
        st.info("Upload data and select scale items to generate the analysis report.")
    st.markdown("---")
    st.markdown("#### Reporting notes")
    st.markdown(
        """
        - Descriptives use available observations per item; standard deviations use the sample estimate (ddof = 1).
        - Kurtosis is reported as excess kurtosis, for which a normal distribution has a value of 0.
        - Shapiro–Wilk tests are presented with visual histograms and normal Q–Q plots; statistical significance is not a standalone diagnostic.
        - Cronbach's alpha uses listwise-complete responses and is reported with a 95% confidence interval.
        - EFA uses a minimum-residual extraction with the selected rotation and listwise-complete responses. Eigenvalue > 1 is shown as a heuristic, not a prescriptive factor-retention decision.
        - CFA uses a researcher-reviewed simple-structure model and maximum likelihood (MLW); selected responses are treated as approximately continuous. The factor assignments, estimator, fit indices, standardized estimates, and analysis n are included in the report.
        - For ordinal Likert items, justify the continuous-indicator approximation or use an ordinal estimator in a separately documented analysis.
        - The report is a computational output, not a claim of APA JARS compliance by itself. Researchers should document sampling, item wording, scoring, missing-data decisions, estimators, and interpretation in the manuscript.
        """
    )

  

  
  
 
  


 
