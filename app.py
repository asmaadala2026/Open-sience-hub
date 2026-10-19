import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="Psychometric Open Science & JARS Suite",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Styling
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
        text-align: center; padding: 20px;
        background: linear-gradient(135deg, #0284C7, #EA580C);
        color: white; border-radius: 12px; margin-bottom: 25px;
    }
    .author-badge {
        font-size: 14px; font-weight: bold; background-color: rgba(255,255,255,0.2);
        padding: 5px 10px; border-radius: 20px; display: inline-block; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Sidebar Language Configuration
st.sidebar.markdown("### 🌐 Language / اللغة")
lang_selection = st.sidebar.selectbox("Language Config", ["English", "Arabic", "French", "Spanish", "German"], label_visibility="collapsed")
lang_map = {"English": "en", "Arabic": "ar", "French": "fr", "Spanish": "es", "German": "de"}
current_lang = lang_map[lang_selection]

# 4. Multilingual Content Dictionary
translations = {
    'en': {
        'dir': 'ltr', 'title': '🚀 Psychometric Open Science Hub',
        'subtitle': 'Scale Development Data Analyzer & JARS-Quant Suite',
        'welcome': 'Welcome to the advanced open-source validation platform designed for psychometric scale development. This engine strictly applies Open Science concepts and automated JARS-Quant (APA) guidelines to verify evaluation instruments.',
        'up_label': 'Upload Dataset (CSV or Excel Format):',
        'preview': '✅ Raw Data Matrix Verification (Open Science Framework)',
        'stats': '📊 JARS Automated Descriptive Analytics Suite',
        'empty': 'Please upload a statistical evaluation file or activate the persistent demo scale below.',
        'success': 'Dataset structure parsed and verified successfully!',
        's_size': 'Total Active Sample Size (N):', 'missing': 'Identified Missing Values:',
        'desc_title': 'Item Descriptives (Means, SDs, Ranges)', 'viz_title': 'Visual Item Distribution Auditor',
        'var_select': 'Select psychometric variable to check distribution matrix:',
        'alpha_title': '🔒 Scale Reliability Matrix Analysis',
        'alpha_label': 'Calculated Internal Consistency (Cronbach\'s Alpha Index):',
        'corr_title': '📈 Inter-Item Pearson Correlation Matrix',
        'dedication_title': '❤️ Special Dedication & Honoring Page',
        'menu_dashboard': '📊 Analysis Dashboard',
        'demo_btn': '⚙️ Load Asmaa Dala\'s Integrated Psychometric Scale (Demo tool)',
        'by_label': 'Developed by: Asmaa Dala'
    },
    'ar': {
        'dir': 'rtl', 'title': '🚀 المنصة السيكومترية للعلم المفتوح',
        'subtitle': 'محلل بيانات تطوير أدوات القياس وحزمة الامتثال لمعايير JARS-Quant',
        'welcome': 'مرحباً بكم في المنصة المفتوحة المتقدمة والمخصصة لتطوير وتدقيق أدوات القياس والمقاييس النفسية والتربوية. تطبق هذه المنصة بصرامة مفاهيم العلم المفتوح وتوجيهات معايير JARS-Quant الدولية لضمان جودة النشر العلمي.',
        'up_label': 'ارفع ملف البيانات الخام لأداة القياس (بصيغة Excel أو CSV):',
        'preview': '✅ فحص وتدقيق مصفوفة البيانات الخام (مبدأ العلم المفتوح)',
        'stats': '📊 حزمة التحليلات الوصفية الآلية وفق معايير JARS الأكاديمية',
        'empty': 'الرجاء رفع ملف البيانات الإحصائية الخام أو الضغط لأسفل لتفعيل أداة القياس المدمجة كعينة تجريبية دائمة.',
        'success': 'تم تحميل ملف البيانات وفك التشفير الهيكلي بنجاح!',
        's_size': 'حجم العينة الإجمالي الفعلي (N):', 'missing': 'إجمالي القيم المفقودة المكتشفة:',
        'desc_title': 'الإحصاء الوصفي للفقرات (المتوسطات، الانحرافات المعيارية، المدى)',
        'viz_title': 'التوزيع التكراري البصري لفقرات المقياس',
        'var_select': 'اختر الفقرة أو البعد لمعاينة مصفوفة توزيعه البصري:',
        'alpha_title': '🔒 تحليل الثبات والاتساق الداخلي للمقياس',
        'alpha_label': 'معامل ثبات ألفا كرونباخ المحسوب للأداة:',
        'corr_title': '📈 مصفوفة ارتباط بيرسون الإحصائية بين أبعاد وفقرات الأداة',
        'dedication_title': '❤️ صفحة إهداء وتكريم أكاديمية خاصة',
        'menu_dashboard': '📊 لوحة التحكم الإحصائية',
        'demo_btn': '⚙️ تفعيل أداة قياس الباحثة أسماء دالة المدمجة (عينة تجريبية ثابتة)',
        'by_label': 'تطوير الباحثة: أسماء دالة'
    },
    'fr': { 'dir': 'ltr', 'title': '🚀 Hub Psychométrique de Science Ouverte', 'subtitle': 'Analyseur de Donnees de Validation & Suite JARS-Quant', 'welcome': 'Bienvenue sur la plateforme psychometrique open source.', 'up_label': 'Charger le jeu de donnees (CSV ou Excel):', 'preview': '✅ Verification des Donnees Brutes', 'stats': '📊 Suite d Analyse Descriptive JARS', 'empty': 'Veuillez charger un fichier ou activer la demo.', 'success': 'Structure des donnees analysee!', 's_size': 'Echantillon (N):', 'missing': 'Valeurs manquantes:', 'desc_title': 'Statistiques Descriptives', 'viz_title': 'Distribution des Items', 'var_select': 'Choisir la variable:', 'alpha_title': '🔒 Analyse de Fiabilite', 'alpha_label': 'Alpha de Cronbach:', 'corr_title': '📈 Matrice de Correlation de Pearson', 'dedication_title': '❤️ Page de Dedicace Speciale', 'menu_dashboard': '📊 Tableau de Bord', 'demo_btn': '⚙️ Charger l\'echelle de Asmaa Dala (Demo)', 'by_label': 'Developed by: Asmaa Dala' },
    'es': { 'dir': 'ltr', 'title': '🚀 Centro Psicometrico de Ciencia Abierta', 'subtitle': 'Anailzador de Desarrollo de Escalas & Suite JARS-Quant', 'welcome': 'Bienvenido a la plataforma de validacion psicometrica.', 'up_label': 'Cargar el conjunto de datos (CSV o Excel):', 'preview': '✅ Verificacion de Matriz de Datos Brutos', 'stats': '📊 Suite de Analisis Descriptivo JARS', 'empty': 'Cargue un archivo o active el instrumento psicometrico.', 'success': '¡Matriz de datos estructurada!', 's_size': 'Muestra (N):', 'missing': 'Valores perdidos:', 'desc_title': 'Analisis Descriptivo', 'viz_title': 'Distribucion de Items', 'var_select': 'Seleccionar variable:', 'alpha_title': '🔒 Confiabilidad Interna', 'alpha_label': 'Alfa de Cronbach:', 'corr_title': '📈 Matriz de Correlacion de Pearson', 'dedication_title': '❤️ Pagina de Dedicatoria Especial', 'menu_dashboard': '📊 Panel de Analisis', 'demo_btn': '⚙️ Cargar escala de Asmaa Dala (Demo)', 'by_label': 'Developed by: Asmaa Dala' },
    'de': { 'dir': 'ltr', 'title': '🚀 Psychometrischer Open Science Hub', 'subtitle': 'Skalenentwicklung & JARS-Quant Suite', 'welcome': 'Willkommen auf der psychometrischen Validierungsplattform.', 'up_label': 'Psychometrischen Datensatz hochladen (CSV/Excel):', 'preview': '✅ Rohdatenmatrix-Ueberpruefung', 'stats': '📊 Deskriptive JARS-Analysesuite', 'empty': 'Bitte laden Sie eine Datei hoch oder nutzen Sie die Demo.', 'success': 'Datensatzstruktur verifiziert!', 's_size': 'Stichprobe (N):', 'missing': 'Fehlende Werte:', 'desc_title': 'Deskriptive Statistik', 'viz_title': 'Visueller Itemverteilungsprüfer', 'var_select': 'Variable auswaehlen:', 'alpha_title': '🔒 Skalenzuverlaessigkeitsanalyse', 'alpha_label': 'Cronbachs Alpha:', 'corr_title': '📈 Pearson-Korrelationsmatrix', 'dedication_title': '❤️ Besondere Widmungsseite', 'menu_dashboard': '📊 Analyse-Dashboard', 'demo_btn': '⚙️ Asmaa Dalas psychometrische Skala laden (Demo)', 'by_label': 'Developed by: Asmaa Dala' }
}

t = translations[current_lang]

if t['dir'] == 'rtl':
    st.markdown('<div style="text-align: right; direction: rtl;">', unsafe_allow_html=True)

# 5. Sidebar Navigation
st.sidebar.write("---")
st.sidebar.markdown(f"### Menu Menu")
page_route = st.sidebar.radio("Navigation Interface", [t['menu_dashboard'], t['dedication_title']], label_visibility="collapsed")

# 6. Execution Block
if page_route == t['menu_dashboard']:
    st.markdown(f"""
    <div class="logo-container">
        <h2 style="color: white !important; margin: 0; font-size: 26px;">{t['title']}</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 13px;">{t['subtitle']}</p>
        <div class="author-badge">{t['by_label']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(t['welcome'])
    st.write("---")
    
    st.markdown(f"### {t['up_label']}")
    uploaded_psych_file = st.file_uploader("Psych File Drop", type=["csv", "xlsx"], label_visibility="collapsed")
    load_demo = st.button(t["demo_btn"])
    
    df = pd.DataFrame()
    if uploaded_psych_file is not None:
        try:
            if uploaded_psych_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_psych_file)
            else:
                df = pd.read_csv(uploaded_psych_file)
        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
    elif load_demo:
        st.session_state['demo_loaded'] = True

    if st.session_state.get('demo_loaded', False) and df.empty:
        np.random.seed(42)
        demo_data = {
            'Item_1': np.random.choice([1, 2, 3, 4, 5], size=150, p=[0.1, 0.1, 0.3, 0.4, 0.1]),
            'Item_2': np.random.choice([1, 2, 3, 4, 5], size=150, p=[0.05, 0.15, 0.4, 0.3, 0.1]),
            'Item_3': np.random.choice([1, 2, 3, 4, 5], size=150, p=[0.1, 0.2, 0.3, 0.2, 0.2]),
            'Item_4': np.random.choice([1, 2, 3, 4, 5], size=150, p=[0.05, 0.1, 0.5, 0.25, 0.1]),
            'Item_5': np.random.choice([1, 2, 3, 4, 5], size=150, p=[0.1, 0.2, 0.4, 0.2, 0.1])
        
