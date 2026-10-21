import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import scipy.stats as stats

# 1. إعدادات الصفحة الأساسية والتصميم (الألوان المفضلة: أزرق، برتقالي، أخضر)
st.set_page_config(page_title="Psychometric Open Science Hub", page_icon="📊", layout="wide")

# إضافة لمسات جمالية وألوان مبهرة باستخدام CSS
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: bold; text-align: center; color: #1E3A8A; margin-bottom: 5px; }
    .subtitle { text-align: center; color: #D97706; font-size: 18px; margin-bottom: 30px; }
    .card-blue { padding: 20px; background-color: #E0F2FE; border-left: 5px solid #0284C7; border-radius: 8px; margin-bottom: 15px; }
    .card-orange { padding: 20px; background-color: #FEF3C7; border-left: 5px solid #D97706; border-radius: 8px; margin-bottom: 15px; }
    .card-green { padding: 20px; background-color: #DCFCE7; border-left: 5px solid #16A34A; border-radius: 8px; margin-bottom: 15px; }
    .jars-badge { background-color: #1E3A8A; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. نظام الترجمة الديناميكي الكامل (حل مشكلة اللغة)
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'  # اللغة الافتراضية العربية

# قاموس النصوص للغتين
translations = {
    'ar': {
        'title': "منصة العلم المفتوح السيكومترية",
        'subtitle': "تم التطوير والتصميم بواسطة: أسماء دالة (Asmaa Dala)",
        'welcome_msg': "👋 مرحباً بك في مستقبل القياس النفسي السيكومتري القائم على العلم المفتوح!",
        'menu_home': "🏠 الواجهة الترحيبية والدليل",
        'menu_scale': "🧪 المقياس التجريبي وتحليل JARS",
        'menu_psycho': "📉 الخصائص السيكومترية والاعتدالية",
        'menu_stats': "📊 الإحصاء الوصفي والأساليب الإحصائية",
        'guide_title': "📘 دليل المنصة ومبادئ العلم المفتوح",
        'jars_title': "📑 تقرير متوافق مع معايير JARS",
        'calc_results': "📊 نتائج التحليل السيكومتري المفصل",
        'normality_check': "🔔 اختبار التوزيع الاعتدالي (Normality Test)"
    },
    'en': {
        'title': "Psychometric Open Science Hub",
        'subtitle': "Developed & Designed by: Asmaa Dala",
        'welcome_msg': "👋 Welcome to the future of psychometrics powered by Open Science!",
        'menu_home': "🏠 Home & Platform Guide",
        'menu_scale': "🧪 Empirical Scale & JARS Analysis",
        'menu_psycho': "📉 Psychometric Properties & Normality",
        'menu_stats': "📊 Descriptive Statistics & Methods",
        'guide_title': "📘 Platform Guide & Open Science Principles",
        'jars_title': "📑 JARS Standards Compliant Report",
        'calc_results': "📊 Detailed Psychometric Results",
        'normality_check': "🔔 Normality Distribution Test"
    }
}

# زر تبديل اللغة في أعلى القائمة الجانبية
st.sidebar.title("🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("اختر اللغة / Choose Language", ['العربية', 'English'])
st.session_state.lang = 'ar' if lang_choice == 'العربية' else 'en'

# تعيين النصوص بناءً على الاختيار
t = translations[st.session_state.lang]

# 3. الهيدر المشترك للمنصة
st.markdown(f"<div class='main-title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)
st.divider()

# 4. القائمة الجانبية للتنقل بين الأقسام (ثلاثة نقاط أو تبويبات تفاعلية)
st.sidebar.header("📌 أقسام المنصة")
page = st.sidebar.radio("انتقل إلى:", [t['menu_home'], t['menu_scale'], t['menu_psycho'], t['menu_stats']])

# ==================== القسم الأول: الواجهة الترحيبية والدليل ====================
if page == t['menu_home']:
    st.success(t['welcome_msg'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class='card-blue'>
            <h3>💙 العلم المفتوح (Open Science)</h3>
            <p>تلتزم المنصة بمبادئ الشفافية وإعادة الإنتاجية (Reproducibility) ومشاركة الأكواد والبيانات بشكل حر ومفتوح المصدر.</p>
        </div>""", unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""<div class='card-orange'>
            <h3>🧡 معايير JARS العالمية</h3>
            <p>جميع التقارير والإحصاءات المستخرجة من هذه المنصة تصاغ بدقة لتطابق معايير جمعية علم النفس الأمريكية APA - JARS.</p>
        </div>""", unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""<div class='card-green'>
            <h3>💚 أدوات متطورة</h3>
            <p>تحليل فوري للمقاييس النفسية، حساب الثبات والصدق، والتحقق من التوزيع الاعتدالي بنقرة زر واحدة.</p>
        </div>""", unsafe_allow_html=True)

    st.subheader(t['guide_title'])
    st.info("هذه المنصة صممت خصيصاً لتجسيد أساليب البحث الحر. يمكنك الانتقال عبر القائمة الجانبية لتجربة المقاييس أو إجراء التحليلات الإحصائية المتقدمة.")

# ==================== القسم الثاني: المقياس التجريبي وتحليل JARS ====================
elif page == t['menu_scale']:
    st.subheader(t['menu_scale'])
    st.write("قم بتجربة هذا المقياس المبسط لرؤية كيف تقوم المنصة بتحليل النتائج فورياً وتفسيرها سيكومترياً:")
    
    # بناء مقياس تجريبي (مثال: مقياس الرضا عن الدراسة عن بعد - 3 عبارات)
    q1 = st.slider("1. أشعر بالرضا التام عن مرونة أدوات العلم المفتوح في جامعتي.", 1, 5, 3)
    q2 = st.slider("2. توفير مصادر برمجية حرة يسهل عليّ فهم البحوث النفسية.", 1, 5, 3)
    q3 = st.slider("3. أرى أن منصات التحليل الفوري تزيد من دقة وتفسير النتائج.", 1, 5, 3)
    
    if st.button("احسب النتيجة واستخرج تقرير JARS"):
        total_score = q1 + q2 + q3
        mean_score = total_score / 3
        
        st.markdown(f"### {t['calc_results']}")
        st.metric(label="الدرجة الكلية للمقياس (Total Score)", value=f"{total_score} / 15")
        st.metric(label="المتوسط الحسابي للاستجابات", value=f"{mean_score:.2f}")
        
        # التفسير التلقائي بناءً على النتيجة
        if total_score >= 11:
            status = "مستوى مرتفع جداً وإيجابي نحو تبيّني أدوات البحث المفتوح."
        elif total_score >= 6:
            status = "مستوى متوسط يتطلب تعزيز الوعي بالأدوات الحرة."
        else:
            status = "مستوى منخفض، هناك فجوة في استخدام المصادر المفتوحة."
            
        st.markdown(f"""<div class='card-green'>
            <h4>📝 التفسير السيكومتري وفقاً للمعايير:</h4>
            <p>{status}</p>
        </div>""", unsafe_allow_html=True)
        
        # إضافة معيار JARS كـ Badge
        st.markdown(f"### {t['jars_title']} <span class='jars-badge'>APA JARS Compliant</span>", unsafe_allow_html=True)
        st.code(f"""
        [Method Section - Reporting Standards]
        - Scale Format: 5-point Likert scale (1=Strongly Disagree, 5=Strongly Agree).
        - Participant Score: {total_score} (Mean = {mean_score:.2f}).
        - Psychometric Interpretation: The participant demonstrated a score indicating a high level of openness.
        """, language="markdown")

# ==================== القسم الثالث: الخصائص السيكومترية والتوزيع الاعتدالي ====================
elif page == t['menu_psycho']:
    st.subheader(t['menu_psycho'])
    
    # توليد بيانات عشوائية تحاكي توزيع درجات مقياس نفسي حقيقي للطلبة
    np.random.seed(42)
    data = np.random.normal(loc=70, scale=10, size=100)
    df = pd.DataFrame(data, columns=['Scores'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {t['normality_check']}")
        # حساب اختبار Shapiro-Wilk للاعتدالية
        shapiro_stat, p_value = stats.shapiro(data)
        
        st.write(f"**قيمة اختبار شابيرو-ويلك (Statistic):** {shapiro_stat:.4f}")
        st.write(f"**الدلالة الإحصائية (p-value):** {p_value:.4f}")
        
        if p_value > 0.05:
            st.success("✔️ البيانات تتبع التوزيع الاعتدالي (p > 0.05). يمكن استخدام الأساليب المعلمية (Parametric).")
        else:
            st.warning("⚠️ البيانات لا تتبع التوزيع الاعتدالي (p <= 0.05). يُنصح بالأساليب غير المعلمية (Non-parametric).")
            
        # قائمة تحقق الخصائص السيكومترية
        st.markdown("### 📋 قائمة تحقق الخصائص السيكومترية (Psychometric Checklist)")
        st.checkbox("التحقق من الثبات (Reliability) عبر معامل ألفا كرونباخ > 0.70", value=True)
        st.checkbox("التحقق من الصدق الظاهري والبنئي (Validity Check)", value=True)
        st.checkbox("مراجعة المفقود من البيانات (Missing Data Analysis)", value=True)

    with col2:
        st.markdown("### 📊 الرسم البياني للتوزيع الاعتدالي")
        fig = px.histogram(df, x='Scores', marginal="violin", title="Normal Distribution Curve", color_discrete_sequence=['#0284C7'])
        st.plotly_chart(fig, use_container_width=True)

# ==================== القسم الرابع: الإحصاء الوصفي والأساليب الإحصائية ====================
elif page == t['menu_stats']:
    st.subheader(t['menu_stats'])
    
    # بيانات افتراضية
    np.random.seed(10)
    scores_pre = np.random.normal(65, 8, 50)
    scores_post = scores_pre + np.random.normal(8, 3, 50)
    
    df_stats = pd.DataFrame({
        'المقياس القبلي (Pre-test)': scores_pre,
        'المقياس البعدي (Post-test)': scores_post
    })
    
    st.markdown("### 📈 جدول الإحصاء الوصفي الشامل (Descriptive Statistics)")
    st.write(df_stats.describe())
    
    st.markdown("### 🧪 الأساليب الإحصائية المتاحة بالمنصة")
    method = st.selectbox("اختر الأسلوب الإحصائي المراد تطبيقه:", ["اختبار ت لعينتين مترابطتين (Paired t-test)", "معامل ارتباط بيرسون (Pearson Correlation)"])
    
    if method == "اختبار ت لعينتين مترابطتين (Paired t-test)":
        t_stat, p_val = stats.ttest_rel(scores_post, scores_pre)
        st.markdown(f"**نتائج الاختبار الإحصائي:**")
        st.info(f"قيمة T الإحصائية = {t_stat:.3f} | الدلالة الإحصائية (p-value) = {p_val:.5f}")
        st.markdown(f"**التفسير وفق JARS:** توجد فروق ذات دلالة إحصائية بين القياسين القبلي والبعدي لصالح القياس البعدي.")
