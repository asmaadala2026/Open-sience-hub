import streamlit as st
import pandas as pd
import io

# Safe initialization for SPSS processing via pyreadstat
try:
    import pyreadstat
except ImportError:
    pyreadstat = None

# 1. Page Configuration
st.set_page_config(page_title="Open Science & JARS Suite", page_icon="📊", layout="centered")

# 2. Custom CSS Styling for a High-End Academic Look
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #2F3E46; }
    [data-testid="stSidebar"] { background-color: #E0F2FE; border-right: 2px solid #BAE6FD; }
    h1 { color: #0369A1 !important; font-family: 'Segoe UI', sans-serif; }
    h2, h3, h4 { color: #EA580C !important; }
    .stButton>button {
        background-color: #16A34A !important; color: white !important;
        border-radius: 8px !important; border: none !important;
        font-weight: bold; transition: 0.3s; width: 100%;
    }
    .stButton>button:hover { background-color: #15803D !important; }
    .logo-container {
        text-align: center; padding: 15px;
        background: linear-gradient(135deg, #0284C7, #EA580C);
        color: white; border-radius: 12px; margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Simple Sidebar Language Setup
st.sidebar.markdown("### 🌐 Language / اللغة")
lang = st.sidebar.selectbox("Select", ["English", "Arabic", "French", "Spanish", "German"], label_visibility="collapsed")

# 4. Dictionary containing interface translations and reporting labels
texts = {
    "English": {
        "title": "🚀 Academic Open Science Hub", "sub": "Data Analyzer & JARS Compliance Suite",
        "up_label": "Upload Dataset (SPSS .sav, Jamovi/CSV, Excel)", "preview": "✅ Raw Data Preview (Open Science Principle)",
        "stats": "📊 JARS Statistical Reporting Automation (APA Standards)", "empty": "Please upload an SPSS or Jamovi dataset file to begin verification.",
        "success": "File parsed successfully!", "s_size": "Sample Size (JARS N):", "missing": "Missing Values Checked:",
        "desc_title": "Descriptive Analytics (Means & SDs)", "viz_title": "Data Distribution Visualizer", "var_select": "Choose variable to check distribution:"
    },
    "Arabic": {
        "title": "🚀 منصة العلم المفتوح الأكاديمية", "sub": "محلل البيانات وحزمة الامتثال لمعايير JARS",
        "up_label": "ارفع ملف البيانات (SPSS .sav, Jamovi/CSV, Excel)", "preview": "✅ معاينة البيانات الخام (مبدأ العلم المفتوح)",
        "stats": "📊 تقارير إحصائية آلية وفق معايير JARS (توجيهات APA)", "empty": "الرجاء رفع ملف بيانات SPSS أو Jamovi لبدء التدقيق الإحصائي والامتثال.",
        "success": "تم تحميل الملف وفك ترميز البيانات بنجاح!", "s_size": "حجم العينة الإجمالي (N):", "missing": "فحص القيم المفقودة المستبعدة:",
        "desc_title": "الإحصاء الوصفي (المتوسطات والانحرافات المعيارية)", "viz_title": "المعاينة البصرية لتوزيع البيانات", "var_select": "اختر المتغير لفحص توزيعه التكراري:"
    },
    "French": {
        "title": "🚀 Hub Académique de Science Ouverte", "sub": "Analyseur de Donnees et Conformite JARS",
        "up_label": "Charger des donnees (SPSS .sav, Jamovi/CSV, Excel)", "preview": "✅ Apercu des Donnees Brutes (Science Ouverte)",
        "stats": "📊 Automatisation des Rapports Statistiques JARS", "empty": "Veuillez charger un fichier pour verifier la conformite.",
        "success": "Fichier traite avec succes!", "s_size": "Taille de l echantillon (N):", "missing": "Valeurs manquantes:",
        "desc_title": "Statistiques Descriptives", "viz_title": "Visualisation de Distribution", "var_select": "Choisir la variable:"
    },
    "Spanish": {
        "title": "🚀 Centro Academico de Ciencia Abierta", "sub": "Analizador de Datos y Cumplimiento de JARS",
        "up_label": "Cargar datos (SPSS .sav, Jamovi/CSV, Excel)", "preview": "✅ Vista Previa de Datos Brutos",
        "stats": "📊 Automatizacion de Informes Estadisticos JARS", "empty": "Cargue un archivo para comenzar la evaluacion de criterios.",
        "success": "Archivo cargado con exito!", "s_size": "Tamano de la muestra (N):", "missing": "Valores perdidos detectados:",
        "desc_title": "Analisis Descriptivo", "viz_title": "Visualizador de Distribucion", "var_select": "Seleccionar variable:"
    },
    "German": {
        "title": "🚀 Akademischer Open Science Hub", "sub": "Datenanalysator & JARS-Konformitaet",
        "up_label": "Datensatz hochladen (SPSS .sav, Jamovi/CSV, Excel)", "preview": "✅ Rohdaten-Vorschau (Open Science)",
        "stats": "📊 JARS Statistische Berichterstattung Automatisierung", "empty": "Bitte laden Sie eine Datendatei hoch, um die Konformitaet zu pruefen.",
        "success": "Datei erfolgreich geladen!", "s_size": "Stichprobenumfang (N):", "missing": "Fehlende Werte:",
        "desc_title": "Deskriptive Statistik", "viz_title": "Datenverteilung visualisieren", "var_select": "Variable auswaehlen:"
    }
}

t = texts[lang]

# Enable Right-to-Left formatting block for Arabic alignment layout
if lang == "Arabic":
    st.markdown('<div style="text-align: right; direction: rtl;">', unsafe_allow_html=True)

# Main Dashboard Banner Configuration
st.markdown(f'<div class="logo-container"><h2 style="color:white!important;margin:0;">{t["title"]}</h2><p style="margin:5px 0 0 0;opacity:0.9;">{t["sub"]}</p></div>', unsafe_allow_html=True)

# 5. File Drag-and-Drop Receiver Interface
st.markdown(f"### {t['up_label']}")
uploaded_file = st.file_uploader("Data Upload Terminal", type=["sav", "csv", "xlsx"], label_visibility="collapsed")

if uploaded_file is not None:
    file_name = uploaded_file.name
    df = pd.DataFrame()
    
    try:
        if file_name.endswith('.sav'):
            if pyreadstat is not None:
                file_bytes = uploaded_file.read()
                df, meta = pyreadstat.read_sav(io.BytesIO(file_bytes))
            else:
                st.error("SPSS file streaming engine initialization failure. Please parse using CSV formatting.")
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
            
        if not df.empty:
            st.success(t["success"])
            
            # --- SHOWCASING OPEN SCIENCE PRINCIPLE ---
            st.markdown(f"### {t['preview']}")
            st.dataframe(df.head(10))
            st.write("---")
            
            # --- DEPLOYING JARS STANDARDS CHECK ---
            st.markdown(f"### {t['stats']}")
            
            # Metric Summary Cards Generation
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=t["s_size"], value=int(df.shape[0]))
            with col2:
                st.metric(label=t["missing"], value=int(df.isna().sum().sum()))
            
            # Automation of descriptive table calculations
            st.markdown(f"#### {t['desc_title']}")
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                st.write(numeric_df.describe().T[['mean', 'std', 'min', 'max']])
                
                # Visual Distribution Showcase Component
                st.markdown(f"#### {t['viz_title']}")
                st.write(t['var_select'])
                target_col = st.selectbox("Column Picker", numeric_df.columns, label_visibility="collapsed")
                st.bar_chart(numeric_df[target_col].head(50))
            else:
                st.info("No explicit numerical values found within the processed file structure to calculate averages.")
                
    except Exception as e:
        st.error(f"Error parsing database mapping: {str(e)}")
else:
    st.info(t["empty"])

# 6. Functional Sidebar Evaluation Feedback Node
st.sidebar.write("---")
st.sidebar.markdown("#### 💡 Suggestions & Feedback / الاقتراحات")
feedback = st.sidebar.text_area("Feedback Box Terminal", height=80, label_visibility="collapsed")
if st.sidebar.button("Submit / إرسال"):
    if feedback:
        st.sidebar.toast("Thank you / شكراً لك!", icon="✨")

if lang == "Arabic":
    st.markdown('</div>', unsafe_allow_html=True)
    
