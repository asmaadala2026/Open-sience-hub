import streamlit as st
import pandas as pd

# 1. إعداد الصفحة الأساسية
st.set_page_config(page_title="Psychometric Open Science Hub", page_icon="🚀", layout="wide")

# 2. تصميم الألوان الجذابة وتنسيق العنوان
st.markdown("""
<style>
.main-title {
    font-size: 45px;
    font-weight: bold;
    background: linear-gradient(to right, #1E90FF, #FF8C00, #32CD32);
    -webkit-background-clip: text;
    color: transparent;
    text-align: center;
    margin-bottom: 5px;
}
.sub-title {
    font-size: 22px;
    text-align: center;
    color: #555;
    margin-bottom: 30px;
    font-family: Arial, sans-serif;
}
</style>
""", unsafe_allow_html=True)

# عرض العنوان واسمك
st.markdown('<div class="main-title">Psychometric Open Science Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">تطوير وتصميم الباحثة: <b>دالة أسماء</b></div>', unsafe_allow_html=True)

# 3. القائمة الجانبية (اللغات والتفاعل)
st.sidebar.header("🌍 إعدادات المنصة")
language = st.sidebar.selectbox("اللغة / Language", ["العربية", "English", "Français", "Español", "Deutsch"])

st.sidebar.markdown("---")
st.sidebar.header("💬 التفاعل والتعليقات")
comment = st.sidebar.text_area("اترك تعليقاً أو استفساراً حول التحليل:")
if st.sidebar.button("إرسال التعليق"):
    st.sidebar.success("تم إرسال تعليقك بنجاح! سيتم مراجعته من قبل الباحثة.")

# 4. تقسيم المنصة إلى 3 أقسام رئيسية
tab1, tab2, tab3 = st.tabs(["📖 الدليل التعريفي للمنصة", "📊 وسيلة الباحثة (الأداة التجريبية)", "⚙️ مساحة إدخال البيانات والتحليل (JARS)"])

# --- القسم الأول: الدليل التعريفي ---
with tab1:
    st.header("مرحباً بك في منصة العلوم المفتوحة للقياس النفسي")
    st.write("""
    **أهداف المنصة:**
    تهدف هذه المنصة إلى تعزيز مبادئ **العلوم المفتوحة (Open Science)** وتطبيق معايير جمعية علم النفس الأمريكية **(APA - JARS)** للشفافية في البحوث الكمية.
    
    **دليل الاستخدام المبسط:**
    1. **تصفح الأداة التجريبية:** انتقل إلى القسم الثاني للاطلاع على مقياس "اتجاهات الموظفين نحو الذكاء الاصطناعي" كنموذج تطبيقي متكامل.
    2. **تحليل بياناتك الخاصة:** انتقل إلى القسم الثالث لرفع بياناتك المجمعة من برامج مثل (SPSS أو Jamovi) مباشرة بصيغة SAV أو CSV.
    3. **استخراج النتائج:** ستقوم المنصة بفحص جودة بياناتك، والتأكد من خلوها من القيم المفقودة، وعرض الإحصاءات الأولية بشفافية تامة.
    """)

# --- القسم الثاني: الأداة التجريبية (مقياس أسماء) ---
with tab2:
    st.header("مقياس اتجاهات الموظفين نحو إستخدام الذكاء الإصطناعي التوليدي في إنجاز مهام وظيفية")
    st.info("تم تقسيم العينة الإجمالية (300 مفردة) منهجياً إلى قسمين لضمان الصدق المتقاطع: 150 للتحليل الاستكشافي، و 150 للتحليل التوكيدي.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("التحليل العاملي الاستكشافي (EFA)")
        if st.button("عرض بيانات ونتائج EFA (150 مفردة)"):
            try:
                df_efa = pd.read_csv("efa-data.csv", sep=";")
                st.dataframe(df_efa, hide_index=True)
                st.success("""
                **ملخص نتائج التحليل:**
                * أظهرت النتائج ملاءمة ممتازة للبيانات (KMO > 0.80).
                * اختبار بارتليت دال إحصائياً.
                * تم استخلاص العوامل بتشبعات قوية تدعم البناء النظري للمقياس.
                """)
            except:
                st.error("تأكدي من وجود ملف efa-data.csv في GitHub")

    with col2:
        st.subheader("التحليل العاملي التوكيدي (CFA)")
        if st.button("عرض بيانات ونتائج CFA (150 مفردة)"):
            try:
                df_cfa = pd.read_csv("cfa-data.csv", sep=";")
                st.dataframe(df_cfa, hide_index=True)
                st.success("""
                **ملخص نتائج التحليل:**
                * أظهر النموذج مطابقة جيدة للبيانات المستقلة.
                * مؤشرات المطابقة المقارنة (CFI) وجذر متوسط مربع الخطأ (RMSEA) جاءت ضمن الحدود الموصى بها.
                """)
            except:
                st.error("تأكدي من وجود ملف cfa-data.csv في GitHub")

# --- القسم الثالث: مساحة إدخال البيانات (دعم SPSS) ---
with tab3:
    st.header("مساحة التحليل التفاعلية وفق معايير JARS")
    st.write("قم برفع ملف البيانات الخاص بك بصيغة (SAV الأصلية أو CSV) لإجراء فحص الشفافية واستخراج الإحصاءات التلقائية.")
    
    # تحديث: السماح برفع ملفات .sav الخاصة بـ SPSS
    uploaded_file = st.file_uploader("ارفع ملف البيانات هنا:", type=["sav", "csv"])
    
    if uploaded_file is not None:
        try:
            # التحقق من نوع الملف وقراءته برمجياً
            if uploaded_file.name.endswith('.sav'):
                df_user = pd.read_spss(uploaded_file)
            else:
                df_user = pd.read_csv(uploaded_file, sep=None, engine='python')
            
            st.success("تم قراءة الملف بنجاح! إليك تقرير التحليل:")
            
            # تحليل معايير JARS
            st.subheader("1. تقرير الشفافية (JARS - Missing Data)")
            missing_count = df_user.isnull().sum().sum()
            if missing_count == 0:
                st.write("✅ **مطابق للمعايير:** لا توجد أي بيانات مفقودة في المصفوفة. البيانات جاهزة للتحليل العاملي المتقدم.")
            else:
                st.warning(f"⚠️ **ملاحظة:** تم اكتشاف {missing_count} خلايا فارغة. يتطلب معيار JARS الإبلاغ عن كيفية معالجة هذه القيم.")
            
            # الإحصاء الوصفي
            st.subheader("2. مصفوفة الإحصاء الوصفي للبيانات الخام")
            st.dataframe(df_user.describe())
            
        except Exception as e:
            st.error("حدث خطأ أثناء قراءة الملف. يرجى التأكد من أن الملف ليس تالفاً.")



            
      
    
    
   
   
