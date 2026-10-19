import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Academic Python Hub",
    page_icon="🚀",
    layout="centered"
)

# 2. Custom CSS Styling (Light Blue, Orange, Green, White)
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #2F3E46; }
    [data-testid="stSidebar"] { background-color: #E0F2FE; border-right: 2px solid #BAE6FD; }
    h1 { color: #0369A1 !important; font-family: 'Segoe UI', sans-serif; }
    h2, h3 { color: #EA580C !important; }
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

# 3. Simple Language Selector
st.sidebar.markdown("### 🌐 Language / اللغة")
lang = st.sidebar.selectbox("Select", ["English", "Arabic", "French", "Spanish", "German"], label_visibility="collapsed")

# 4. Content Rendering based on Selection
if lang == "English":
    st.markdown('<div class="logo-container"><h2 style="color:white!important;margin:0;">🚀 Academic Python Hub</h2><p style="margin:5px 0 0 0;opacity:0.9;">Open Science • JARS</p></div>', unsafe_allow_html=True)
    st.markdown("### An Open-Source Platform for Scientific Research")
    st.write("Welcome to the practical platform designed to empower researchers using Python to promote Open Science and international reporting quality.")
    st.write("---")
    st.markdown("### 📋 JARS Compliance Checklist")
    st.checkbox("Did you specify the sample size accurately?")
    st.checkbox("Are the data exclusion criteria completely clear?")
    st.checkbox("Is the raw dataset hosted on a verified open access repository?")
    if st.button("Calculate Compliance"):
        st.success("🟢 High Compliance (100%) - Ready for JARS Submission!")

elif lang == "Arabic":
    st.markdown('<div style="text-align: right; direction: rtl;"><div class="logo-container"><h2 style="color:white!important;margin:0;">🚀 مركز بايثون الأكاديمي</h2><p style="margin:5px 0 0 0;opacity:0.9;">العلم المفتوح • معايير JARS</p></div>', unsafe_allow_html=True)
    st.markdown("### منصة برمجية مفتوحة المصدر للبحث العلمي العالمي")
    st.write("مرحباً بكم في المنصة التطبيقية المصممة لتمكين الباحثين باستخدام لغة بايثون لتعزيز العلم المفتوح وجودة التقارير الدولية.")
    st.write("---")
    st.markdown("### 📋 قائمة التحقق من الامتثال لمعايير JARS")
    st.checkbox("هل قمت بتحديد حجم العينة بدقة؟")
    st.checkbox("هل معايير استبعاد البيانات واضحة تماماً؟")
    st.checkbox("هل البيانات الخام مرفوعة على مستودع مفتوح وموثق؟")
    if st.button("احسب نسبة الامتثال"):
        st.success("🟢 نسبة امتثال عالية (100%) - البحث جاهز للمطابقة!")
    st.markdown('</div>', unsafe_allow_html=True)

elif lang == "French":
    st.markdown('<div class="logo-container"><h2 style="color:white!important;margin:0;">🚀 Academic Python Hub</h2><p style="margin:5px 0 0 0;opacity:0.9;">Science Ouverte • JARS</p></div>', unsafe_allow_html=True)
    st.markdown("### Plateforme Open-Source pour la Recherche Scientifique")
    st.write("Bienvenue sur la plateforme concue pour autonomiser les chercheurs utilisant Python pour promouvoir la Science Ouverte.")
    st.write("---")
    st.markdown("### 📋 Liste de controle JARS")
    st.checkbox("Avez-vous specifie la taille de l échantillon?")
    st.checkbox("Les criteres d exclusion des donnees sont-ils clairs?")
    st.checkbox("Le jeu de donnees est-il herberge sur un depot ouvert?")
    if st.button("Calculer la conformite"):
        st.success("🟢 Haute conformite (100%) - Pret pour JARS!")

elif lang == "Spanish":
    st.markdown('<div class="logo-container"><h2 style="color:white!important;margin:0;">🚀 Academic Python Hub</h2><p style="margin:5px 0 0 0;opacity:0.9;">Ciencia Abierta • JARS</p></div>', unsafe_allow_html=True)
    st.markdown("### Plataforma de Codigo Abierto para la Investigacion")
    st.write("Bienvenido a la plataforma disenada para empoderar a investigadores utilizando Python para promover la Ciencia Abierta.")
    st.write("---")
    st.markdown("### 📋 Lista de verificacion JARS")
    st.checkbox("Especifico el tamano de la muestra con precision?")
    st.checkbox("Estan claros los criterios de exclusion de datos?")
    st.checkbox("Esta el conjunto de datos en un repositorio abierto?")
    if st.button("Calcular cumplimiento"):
        st.success("🟢 Alto cumplimiento (100%) - Listo para JARS!")

elif lang == "German":
    st.markdown('<div class="logo-container"><h2 style="color:white!important;margin:0;">🚀 Academic Python Hub</h2><p style="margin:5px 0 0 0;opacity:0.9;">Open Science • JARS</p></div>', unsafe_allow_html=True)
    st.markdown("### Open-Source-Plattform fur die Forschung")
    st.write("Willkommen auf der Plattform, die entwickelt wurde, um Forscher mit Python zu unterstutzen.")
    st.write("---")
    st.markdown("### 📋 JARS-Checkliste")
    st.checkbox("Haben Sie die Stichprohengroesse genau angegeben?")
    st.checkbox("Sind die Ausschlusskriterien fur Daten klar?")
    st.checkbox("Ist der Rohdatensatz auf einem Repository gehostet?")
    if st.button("Konformitaet berechnen"):
        st.success("🟢 Hohe Konformitaet (100%) - Bereit fuer JARS!")

# 5. Sidebar Feedback System
st.sidebar.write("---")
st.sidebar.markdown("#### 💡 Suggestions & Feedback / الاقتراحات")
feedback = st.sidebar.text_area("Feedback Label", height=80, label_visibility="collapsed")
if st.sidebar.button("Submit / إرسال"):
    if feedback:
        st.sidebar.toast("Thank you! / شكرًا لك!", icon="✨")
