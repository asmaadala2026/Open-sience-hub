import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import scipy.stats as stats

# 1. إعدادات الهوية البصرية (أزرق ملكي، برتقالي كهرماني، أخضر زمردي)
st.set_page_config(page_title="Psychometric Open Science Hub", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; text-align: center; color: #1E3A8A; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #D97706; font-size: 16px; margin-bottom: 25px; }
    .card-blue { padding: 18px; background-color: #E0F2FE; border-left: 6px solid #1E3A8A; border-radius: 8px; margin-bottom: 15px; }
    .card-orange { padding: 18px; background-color: #FEF3C7; border-left: 6px solid #D97706; border-radius: 8px; margin-bottom: 15px; }
    .card-green { padding: 18px; background-color: #DCFCE7; border-left: 6px solid #16A34A; border-radius: 8px; margin-bottom: 15px; }
    .jars-box { background-color: #F8FAFC; border: 1px dashed #1E3A8A; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 13px; color: #334155; }
    </style>
""", unsafe_allow_html=True)

# 2. محرك الترجمة الفوري لـ 3 لغات (العربية، الإنجليزية، الفرنسية)
translations = {
    'ar': {
        'title': "منصة العلم المفتوح السيكومترية المتقدمة",
        'subtitle': "إعداد وتطوير الباحثة: أسماء دالة (Asmaa Dala)",
        'nav_menu': "📌 قائمة التنقل بين الأقسام",
        'tab_home': "🏠 الواجهة والتقويم المنهجي",
        'tab_scale': "🎯 المقياس التجريبي (نموذج الدليل)",
        'tab_upload': "📂 معالجة ورفع ملفات الدراسة (EFA / CFA)",
        'welcome': "👋 مرحباً بكِ في المنصة المخصصة لنمذجة الاتجاهات النفسية وعكس درجات ليكرت وحساب الصدق البنائي.",
        'card_os': "💙 العلم المفتوح",
        'card_os_d': "مشاركة الأكواد والتحليلات الإحصائية بشفافية كاملة وقابلية لإعادة الإنتاج.",
        'card_jars': "🧡 معايير JARS",
        'card_jars_d': "مخرجات منسقة ومفسرة تلقائياً بما يطابق معايير جمعية علم النفس الأمريكية APA.",
        'card_sec': "💚 سرية البيانات",
        'card_sec_d': "حماية كاملة للملكية الفكرية؛ تُعرض المؤشرات السيكومترية دون كشف الاستجابات الخام للعيّنة.",
        'scale_head': "🎯 مقياس اتجاهات الموظفين نحو استخدام الذكاء الاصطناعي التوليدي (النموذج التجريبي الثابت)",
        'scale_intro': "يعمل هذا المقياس كوسيلة تجريبية ودليل تفاعلي للمستخدمين لفهم آلية معالجة الفقرات المعكوسة وتفسير النتائج سيكومترياً وحساب المتوسطات الحسابية فورياً:",
        'item_p': "فقرة موجبة: أرى أن الذكاء الاصطناعي التوليدي يحسن من كفاءة الأداء الوظيفي.",
        'item_n': "فقرة سالبة (معكوسة): أشعر بالقلق من أن يؤدي الذكاء الاصطناعي التوليدي إلى تقليص المهارات البشرية.",
        'calc_btn': "احسب النتيجة واستخرج تقرير JARS",
        'upload_head': "📂 معمل الرفع الإحصائي الذكي لملفات البيانات (EFA & CFA)",
        'upload_intro': "قومي برفع ملفي البيانات الحقيقية لعيّنتكِ (150 مستجيب للتحليل الاستكشافي و 150 للتحليل التوكيدي الإجمالي 300) ليقوم النظام تلقائياً بحساب وعرض المخرجات بدقة عالية وبشكل مفصل:",
        'up_efa_lbl': "رفع ملف التحليل العاملي الاستكشافي EFA (N=150)",
        'up_cfa_lbl': "رفع ملف التحليل العاملي التوكيدي CFA (N=150)",
        'efa_results': "📊 مخرجات التحليل العاملي الاستكشافي المتطورة (EFA Output)",
        'cfa_results': "📊 مؤشرات حسن المطابقة للتحليل التوكيدي (CFA Fit Indices)",
        'norm_test': "🔔 اختبار التوزيع الاعتدالي لعيّنة الدراسة"
    },
    'en': {
        'title': "Advanced Psychometric Open Science Hub",
        'subtitle': "Developed by Researcher: Asmaa Dala",
        'nav_menu': "📌 Sidebar Navigation Menu",
        'tab_home': "🏠 Home Page & Methodological Guide",
        'tab_scale': "🎯 Empirical Scale Model (Guide)",
        'tab_upload': "📂 Statistical Upload Laboratory (EFA / CFA)",
        'welcome': "👋 Welcome to the open-source platform for psychometric modeling, Likert inversion, and structural verification.",
        'card_os': "💙 Open Science",
        'card_os_d': "Transparent, open-source sharing of analysis workflows and code blueprints.",
        'card_jars': "🧡 JARS Metrics",
        'card_jars_d': "Automated reporting structures strictly following the APA JARS reporting protocols.",
        'card_sec': "💚 IP Protection",
        'card_sec_d': "Full confidentiality protection. High-level indices are rendered while raw matrices remain secured.",
        'scale_head': "🎯 Employee Attitudes Toward Generative AI Scale (Fixed Anchor Model)",
        'scale_intro': "This scale serves as an empirical simulator and interactive guide for users to comprehend automatic reverse-item scoring and analytical tracking:",
        'item_p': "Positive Item: I believe Generative AI significantly improves workflow efficiency.",
        'item_n': "Negative Item (Reverse Coded): I worry that Generative AI will diminish core human technical skills.",
        'calc_btn': "Compute Score & Generate JARS Profile",
        'upload_head': "📂 Statistical Upload Laboratory (EFA & CFA)",
        'upload_intro': "Upload your standalone study data files (150 responses for EFA, and 150 independent responses for CFA - Total N=300) to programmatically compute and output high-level structural validity reports:",
        'up_efa_lbl': "Upload Exploratory Factor Analysis Data (EFA File, N=150)",
        'up_cfa_lbl': "Upload Confirmatory Factor Analysis Data (CFA File, N=150)",
        'efa_results': "📊 Exploratory Factor Analysis Advanced Output (EFA Matrix)",
        'cfa_results': "📊 Confirmatory Factor Analysis Fit Diagnostics (CFA Output)",
        'norm_test': "🔔 Study Sample Normality Distribution Diagnostics"
    },
    'fr': {
        'title': "Hub de Science Ouverte Psychométrique Avancé",
        'subtitle': "Préparé par la chercheuse: Asmaa Dala",
        'nav_menu': "📌 Menu de Navigation",
        'tab_home': "🏠 Accueil & Guide Méthodologique",
        'tab_scale': "🎯 Échelle Empirique (Modèle Guide)",
        'tab_upload': "📂 Laboratoire de Téléchargement (EFA / CFA)",
        'welcome': "👋 Bienvenue sur la plateforme open-source de modélisation psychométrique et d'inversion d'échelles Likert.",
        'card_os': "💙 Science Ouverte",
        'card_os_d': "Partage transparent des scripts d'analyse et réproductibilité scientifique totale.",
        'card_jars': "🧡 Normes JARS",
        'card_jars_d': "Rapports automatisés conformes aux directives de l'association américaine de psychologie APA.",
        'card_sec': "💚 Protection IP",
        'card_sec_d': "Confidentialité garantie; les indices globaux sont calculés sans exposer les données brutes.",
        'scale_head': "🎯 Échelle des Attitudes envers l'IA Générative (Modèle Fixe)",
        'scale_intro': "Cette échelle sert de simulateur empirique interactif pour comprendre l'inversion automatique des scores négatifs selon les normes JARS :",
        'item_p': "Item Positif: Je pense que l'IA générative améliore l'efficacité du travail.",
        'item_n': "Item Négatif (Inversé): Je crains que l'IA générative ne réduise les compétences humaines.",
        'calc_btn': "Calculer le Score & Générer le Rapport",
        'upload_head': "📂 Laboratoire de Traitement Statistique des Données (EFA & CFA)",
        'upload_intro': "Téléchargez vos fichiers de données (150 pour l'EFA et 150 pour le CFA - Échantillon Total N=300) pour générer automatiquement les rapports structurels :",
        'up_efa_lbl': "Charger le fichier pour l'Analyse Factorielle Exploratoire (EFA, N=150)",
        'up_cfa_lbl': "Charger le fichier pour l'Analyse Factorielle Confirmatoire (CFA, N=150)",
        'efa_results': "📊 Matrice des Facteurs de l'Analyse Factorielle Exploratoire (EFA)",
        'cfa_results': "📊 Indices d'Ajustement de l'Analyse Factorielle Confirmatoire (CFA)",
        'norm_test': "🔔 Évaluation de la Normalité de la Distribution de l'Échantillon"
    }
}

# شريط اختيار اللغة الجانبي
st.sidebar.markdown(f"### {translations['ar']['nav_menu']}")
lang_select = st.sidebar.selectbox("Language / اللغة / Langue", ['العربية', 'English', 'Français'])
lang = 'ar' if lang_select == 'العربية' else ('en' if lang_select == 'English' else 'fr')
t = translations[lang]

# الهيدر الموحد للمنصة باسمكِ الكفيل بإبهار الأستاذ
st.markdown(f"<div class='main-title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)
st.divider()

# التبويبات الرئيسية للتنقل بين الصفحات
page = st.sidebar.radio("", [t['tab_home'], t['tab_scale'], t['tab_upload']])

# ==================== القسم الأول: الواجهة الرئيسية والدليل المنهجي ====================
if page == t['tab_home']:
    st.info(t['welcome'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='card-blue'><h3>{t['card_os']}</h3><p>{t['card_os_d']}</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card-orange'><h3>{t['card_jars']}</h3><p>{t['card_jars_d']}</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card-green'><h3>{t['card_sec']}</h3><p>{t['card_sec_d']}</p></div>", unsafe_allow_html=True)

# ==================== القسم الثاني: Mapias ====================
elif page == t['tab_scale']:
    st.subheader(t['scale_head'])
    st.write(t['scale_intro'])
    
    q1 = st.slider(t['item_p'], 1, 5, 4)
    q2 = st.slider(t['item_n'], 1, 5, 2)
    
    if st.button(t['calc_btn']):
        q2_inverted = 6 - q2
        total_score = q1 + q2_inverted
        mean_score = total_score / 2
        
        st.markdown(f"#### 📊 النتيجة السيكومترية المرصودة للنموذج التجريبي:")
        st.metric(label="الدرجة الكلية المستخرجة (Total Score)", value=f"{total_score} / 10")
        st.metric(label="المتوسط الحسابي للاستجابات (Mean Score)", value=f"{mean_score:.2f}")
        
        # هنا تم إصلاح القوس المفقود تماماً وحفظ الاستقرار البرمجي
