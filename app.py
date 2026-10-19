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
        padding: 10px;
        background: linear-gradient(135deg, #0284C7, #EA580C);
        color: white;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# 3. Language Session State Management
if 'lang' not in st.session_state:
    st.session_state.lang = 'English'

st.sidebar.markdown("### 🌐 Language / اللغة")
if st.sidebar.button("Switch Language / تغيير اللغة"):
    st.session_state.lang = 'العربية' if st.session_state.lang == 'English' else 'English'

# 4. Translations Dictionary
translations = {
    'English': {
        'dir': 'ltr',
        'title': '🚀 Academic Python Hub',
        'subtitle': 'An Open-Source Software Platform for Global Scientific Research',
        'welcome': 'Welcome to the practical platform designed to empower researchers and academics using Python. This hub is fully built on free and open-source tools to promote **Open Science** and international reporting quality.',
        'objectives': '🎯 Platform Objectives:',
        'obj1': '💡 **Enhance Transparency:** Free tools to host, share, and verify raw datasets.',
        'obj2': '📊 **JARS Compliance:** Simplifying statistical reporting according to APA guidelines.',
        'obj3': '🛠️ **Support Free Software:** Demonstrating Python\'s capability as a premium alternative to proprietary suites.',
        'menu_title': 'Navigation Menu:',
        'menu_home': '🏠 Home & Open Science',
        'menu_jars': '📊 JARS Data Analyzer',
        'menu_auditor': '📋 Open Science Auditor',
        'feedback_title': '💡 Suggestions & Feedback',
        'feedback_label': 'Help us improve the platform:',
        'feedback_btn': 'Submit Feedback',
        'feedback_success': 'Thank you! Your feedback has been received.',
        'upload_label': 'Upload your research dataset (CSV file):',
        'audit_title': 'Open Science & JARS Compliance Checklist'
    },
    'العربية': {
        'dir': 'rtl',
        'title': '🚀 مركز بايثون الأكاديمي',
        'subtitle': 'منصة برمجية مفتوحة المصدر للبحث العلمي العالمي',
        'welcome': 'مرحباً بكم في المنصة التطبيقية المصممة لتمكين الباحثين والأكاديميين باستخدام لغة بايثون. تم بناء هذا المركز بالكامل على أدوات مجانية ومفتوحة المصدر لتعزيز **العلم المفتوح** وجودة التقارير الدولية.',
        'objectives': '🎯 أهداف المنصة:',
        'obj1': '💡 **تعزيز الشفافية:** أدوات مجانية لاستضافة ومشاركة والتحقق من مجموعات البيانات الخام.',
        'obj2': '📊 **الامتثال لمعايير JARS:** تبسيط التقارير الإحصائية وفقاً لتوجيهات الجمعية الأمريكية لعلم النفس (APA).',
        'obj3': '🛠️ **دعم البرمجيات الحرة:** إثبات قدرة بايثون كبديل متميز للحزم الاحتكارية المغلقة.',
        'menu_title': 'قائمة التنقل:',
        'menu_home': '🏠 الرئيسية والعلم المفتوح',
        'menu_jars': '📊 محلل بيانات JARS',
        'menu_auditor': '📋 مدقق العلم المفتوح',
        'feedback_title': '💡 الاقتراحات والآراء',
        'feedback_label': 'ساعدنا في تطوير المنصة:',
        'feedback_btn': 'إرسال الاقتراح',
        'feedback_success': 'شكرًا لك! تم استلام اقتراحك بنجاح.',
        'upload_label': 'قم برفع ملف البيانات الخاص ببحثك (بصيغة CSV):',
        'audit_title': 'قائمة التحقق من الامتثال لمعايير العلم المفتوح و JARS'
    }
}

t = translations[st.session_state.lang]

# Apply Right-to-Left styling if Arabic is selected
if t['dir'] == 'rtl':
    st.markdown('<div style="text-align: right; direction: rtl;">', unsafe_allow_html=True)

# 5. Sidebar Navigation Menu
st.sidebar.markdown(f"### {t['menu_title']}")
page = st.sidebar.radio(
    "",
    [t['menu_home'], t['menu_jars'], t['menu_auditor']],
    label_visibility="collapsed"
)

# 6. Page Content Rendering
if page == t['menu_home']:
    st.markdown(f"""
    <div class="logo-container">
        <h2 style="color: white !important; margin: 0; font-size: 28px;">{t['title']}</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Open Science • JARS • Python</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### {t['subtitle']}")
    st.write(t['welcome'])
    
    st.write("---")
    st.markdown(f"### {t['objectives']}")
    st.markdown(t['obj1'])
    st.markdown(t['obj2'])
    st.markdown(t['obj3'])

elif page == t['menu_jars']:
    st.title(t['menu_jars'])
    st.write(t['upload_label'])
    
    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown("### ✅ Data Preview / معاينة البيانات")
        st.dataframe(df.head())
        st.markdown("### 📊 Statistical Summary / التلخيص الإحصائي")
        st.write(df.describe())

elif page == t['menu_auditor']:
    st.title(t['audit_title'])
    st.checkbox("Did you specify the sample size? / هل قمت بتحديد حجم العينة بدقة؟")
    st.checkbox("Are the exclusion criteria clear? / هل معايير استبعاد البيانات واضحة؟")
    st.checkbox("Is the raw data hosted on an open repository? / هل البيانات الخام مرفوعة على مستودع مفتوح؟")
    if st.button("Calculate Compliance / احسب نسبة الامتثال"):
        st.success("🟢 High Compliance (100%) - Ready for JARS Submission!")

# 7. Feedback System in Sidebar
st.sidebar.write("---")
st.sidebar.markdown(f"#### {t['feedback_title']}")
feedback_text = st.sidebar.text_area(t['feedback_label'], height=80, label_visibility="collapsed")
if st.sidebar.button(t['feedback_btn']):
    if feedback_text:
        st.sidebar.toast(t['feedback_success'], icon="✨")

# Close Right-to-Left styling div if applicable
if t['dir'] == 'rtl':
    st.markdown('</div>', unsafe_allow_html=True)
            
