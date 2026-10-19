import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Academic Python Hub",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS Styling (Light Blue, Orange, Green, White)
st.markdown("""
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #2F3E46;
    }
    [data-testid="stSidebar"] {
        background-color: #E0F2FE;
        border-right: 2px solid #BAE6FD;
    }
    h1 {
        color: #0369A1 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h2, h3 {
        color: #EA580C !important;
    }
    .stButton>button {
        background-color: #16A34A !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #15803D !important;
        box-shadow: 0px 4px 10px rgba(22, 163, 74, 0.3);
    }
    .logo-container {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #0284C7, #EA580C);
        color: white;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 3. Language Selection Component
st.sidebar.markdown("### 🌐 Select Language")
lang_choice = st.sidebar.selectbox(
    "Language Select",
    ["English", "Arabic", "French", "Spanish", "German"],
    label_visibility="collapsed"
)

# Mapping selection to internal language code
lang_map = {
    "English": "en",
    "Arabic": "ar",
    "French": "fr",
    "Spanish": "es",
    "German": "de"
}
current_lang = lang_map[lang_choice]

# 4. Multilingual Dictionary Dataset (All Written in English alphabet)
translations = {
    'en': {
        'dir': 'ltr',
        'title': '🚀 Academic Python Hub',
        'subtitle': 'An Open-Source Software Platform for Global Scientific Research',
        'welcome': 'Welcome to the practical platform designed to empower researchers and academics using Python. This hub is fully built on free and open-source tools to promote Open Science and international reporting quality.',
        'objectives': 'Platform Objectives:',
        'obj1': 'Enhance Transparency: Free tools to host, share, and verify raw datasets.',
        'obj2': 'JARS Compliance: Simplifying statistical reporting according to APA guidelines.',
        'obj3': 'Support Free Software: Demonstrating Pythons capability as a premium alternative to proprietary suites.',
        'menu_title': 'Navigation Menu:',
        'menu_home': 'Home and Open Science',
        'menu_jars': 'JARS Data Analyzer',
        'menu_auditor': 'Open Science Auditor',
        'feedback_title': 'Suggestions and Feedback',
        'feedback_label': 'Help us improve the platform:',
        'feedback_btn': 'Submit Feedback',
        'feedback_success': 'Thank you! Your feedback has been received.',
        'upload_label': 'Upload your research dataset (CSV file):',
        'audit_title': 'Open Science and JARS Compliance Checklist',
        'q1': 'Did you specify the sample size accurately?',
        'q2': 'Are the data exclusion criteria completely clear?',
        'q3': 'Is the raw dataset hosted on a verified open access repository?',
        'calc_btn': 'Calculate Compliance',
        'audit_success': 'High Compliance (100%) - Ready for JARS Submission!'
    },
    'ar': {
        'dir': 'rtl',
        'title': '🚀 Markaz Python Al-Akadimi',
        'subtitle': 'Minassa Barmajiyya Maftouhat Al-Masdar Lil-Bahth Al-Ilmi Al-Alami',
        'welcome': 'Marhaban bikum fi al-minassa al-tatbiqiyya al-musammamah li-tamkin al-bahithin wa al-akadimiyyin bi-istikhdam lughat Python.',
        'objectives': 'Ahdaf Al-Minassa:',
        'obj1': 'Taaziz al-shafafiyya: Adawat majaniyyah li-istidhafat wa musharakat al-bayanat.',
        'obj2': 'Al-imtithal li-maaiir JARS: Tabsit al-taqarir al-ihsaiyyah wifqan li-tawjihat APA.',
        'obj3': 'Dahm al-barmajiyyat al-hurra: Ithbat qudrat Python ka-badil mutamayiz.',
        'menu_title': 'Qaimat Al-Tanaqqul:',
        'menu_home': 'Al-Raisiyyah wa Al-Ilm Al-Maftouh',
        'menu_jars': 'Muhallil Bayanat JARS',
        'menu_auditor': 'Mudaqqiq Al-Ilm Al-Maftouh',
        'feedback_title': 'Al-Iqtirahāt wa Al-Arā',
        'feedback_label': 'Saidna fi tatwir al-minassa:',
        'feedback_btn': 'Irsal Al-Iqtirah',
        'feedback_success': 'Shukran lak! Tam istilam iqtirahuka bi-najah.',
        'upload_label': 'Qum bi-raf milaf al-bayanat (CSV):',
        'audit_title': 'Qaimat al-tahaqquq min al-imtithal li-maaiir JARS',
        'q1': 'Hal qumta bi-tahdid hajm al-ayyinah bi-diqqah?',
        'q2': 'Hal maaiir istibhād al-bayanat wadhihah?',
        'q3': 'Hal al-bayanat al-kham marfouah ala mustawda maftouh?',
        'calc_btn': 'Ihsib Nisbat Al-Imtithal',
        'audit_success': 'Nisbat imtithal aliyah (100%) - Al-bahth jahiz!'
    },
    'fr': {
        'dir': 'ltr',
        'title': '🚀 Academic Python Hub',
        'subtitle': 'Une plateforme logicielle open source pour la recherche scientifique mondiale',
        'welcome': 'Bienvenue sur la plateforme pratique concue pour autonomiser les chercheurs et les universitaires utilisant Python.',
        'objectives': 'Objectifs de la plateforme:',
        'obj1': 'Ameliorer la transparence: Outils gratuits pour herberger et partager les donnees.',
        'obj2': 'Conformite JARS: Simplifier les rapports statistiques selon les directives de l APA.',
        'obj3': 'Soutenir les logiciels libres: Demontrer la capacite de Python comme alternative.',
        'menu_title': 'Menu de navigation:',
        'menu_home': 'Accueil et Science Ouverte',
        'menu_jars': 'Analyseur de donnees JARS',
        'menu_auditor': 'Auditeur de Science Ouverte',
        'feedback_title': 'Suggestions et Commentaires',
        'feedback_label': 'Aidez-nous a ameliorer la plateforme:',
        'feedback_btn': 'Envoyer les commentaires',
        'feedback_success': 'Merci! Vos commentaires ont ete recus.',
        'upload_label': 'Telechargez votre ensemble de donnees de recherche (fichier CSV):',
        'audit_title': 'Liste de controle de conformite Science Ouverte et JARS',
        'q1': 'Avez-vous specifie la taille de l echantillon avec precision?',
        'q2': 'Les criteres d exclusion des donnees sont-ils clairs?',
        'q3': 'Le jeu de donnees brutes est-il herberge sur un depot ouvert verifie?',
        'calc_btn': 'Calculer la conformite',
        'audit_success': 'Haute conformite (100%) - Pret pour la soumission JARS!'
    },
    'es': {
        'dir': 'ltr',
        'title': '🚀 Academic Python Hub',
        'subtitle': 'Una plataforma de software de codigo abierto para la investigacion cientifica global',
        'welcome': 'Bienvenido a la plataforma practica disenada para empoderar a investigadores y academicos utilizando Python.',
        'objectives': 'Objetivos de la plataforma:',
        'obj1': 'Mejorar la transparencia: Herramientas gratuitas para alojar y compartir datos.',
        'obj2': 'Cumplimiento de JARS: Simplificar los informes estadisticos de acuerdo con APA.',
        'obj3': 'Apoyar el software libre: Demostrar la capacidad de Python como alternativa.',
        'menu_title': 'Menu de navegacion:',
        'menu_home': 'Inicio y Ciencia Abierta',
        'menu_jars': 'Analizador de datos JARS',
        'menu_auditor': 'Auditor de Ciencia Abierta',
        'feedback_title': 'Sugerencias y comentarios',
        'feedback_label': 'Ayudanos a mejorar la plataforma:',
        'feedback_btn': 'Enviar comentarios',
        'feedback_success': 'Gracias! Tus comentarios han sido recibidos.',
        'upload_label': 'Cargue su conjunto de datos de investigacion (archivo CSV):',
        'audit_title': 'Lista de verificacion de cumplimiento de Ciencia Abierta y JARS',
        'q1': 'Especifico el tamano de la muestra con precision?',
        'q2': 'Estan claros los criterios de exclusion de datos?',
        'q3': 'Esta el conjunto de datos brutos alojado en un repositorio abierto verificado?',
        'calc_btn': 'Calcular cumplimiento',
        'audit_success': 'Alto cumplimiento (100%) - Listo para JARS!'
    },
    'de': {
        'dir': 'ltr',
        'title': '🚀 Academic Python Hub',
        'subtitle': 'Eine Open-Source-Softwareplattform fur die weltweite wissenschaftliche Forschung',
        'welcome': 'Willkommen auf der praktischen Plattform, die entwickelt wurde, um Forscher und Akademiker mit Python zu unterstutzen.',
        'objectives': 'Ziele der Plattform:',
        'obj1': 'Transparenz verbessern: Kostenlose Tools zum Hosten und Teilen von Rohdaten.',
        'obj2': 'JARS-Konformitat: Vereinfachung der statistischen Berichterstattung nach APA.',
        'obj3': 'Freie Software unterstutzen: Demonstration der Fahigkeiten von Python.',
        'menu_title': 'Navigationsmenu:',
        'menu_home': 'Startseite und Open Science',
        'menu_jars': 'JARS-Datenanalysator',
        'menu_auditor': 'Open Science Auditor',
        'feedback_title': 'Vorschlage und Feedback',
        'feedback_label': 'Helfen Sie uns, die Plattform zu verbessern:',
        'feedback_btn': 'Feedback senden',
        'feedback_success': 'Vielen Dank! Ihr Feedback wurde empfangen.',
        'upload_label': 'Laden Sie Ihren Forschungsdatensatz hoch (CSV-Datei):',
        'audit_title': 'Checkliste fur Open Science und JARS-Konformitat',
        'q1': 'Haben Sie die Stichprobengroesse genau angegeben?',
        'q2': 'Sind die Ausschlusskriterien fur Daten klar?',
        'q3': 'Ist der Rohdatensatz auf einem verifizierten Open-Access-Repository gehostet?',
        'calc_btn': 'Konformitaet berechnen',
        'audit_success': 'Hohe Konformitaet (100%) - Bereit fuer JARS!'
    }
}

t = translations[current_lang]

