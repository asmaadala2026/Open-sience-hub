import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import shapiro
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity

st.set_page_config(page_title="Psychometric Open Science Hub", page_icon="🚀", layout="wide")

# تصميم الواجهة
st.markdown("""
<style>
.main-title { font-size: 45px; font-weight: bold; background: linear-gradient(to right, #1E90FF, #FF8C00, #32CD32); -webkit-background-clip: text; color: transparent; text-align: center; margin-bottom: 5px; }
.sub-title { font-size: 22px; text-align: center; color: #555; margin-bottom: 30px; font-family: Arial, sans-serif; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Psychometric Open Science Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">تطوير وتصميم الباحثة: <b>دالة أسماء</b></div>', unsafe_allow_html=True)

# دالة حساب ألفا كرونباخ برمجياً
def calculate_cronbach_alpha(df):
    df_numeric = df.select_dtypes(include=[np.number])
    k = df_numeric.shape[1]
    if k < 2: return 0
    var_sum = df_numeric.var(ddof=1).sum()
    total_var = df_numeric.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - (var_sum / total_var)) if total_var != 0 else 0

tab1, tab2, tab3 = st.tabs(["📖 الدليل التعريفي", "📊 الأداة التجريبية (مقياس أسماء)", "⚙️ محرك التحليل السيكومتري (الصدق والثبات)"])

# --- القسم الأول والثاني (مختصر للحفاظ على مساحتك) ---
with tab1:
    st.header("مرحباً بك في منصة العلوم المفتوحة للقياس النفسي")
    st.write("المنصة تطبق معايير APA 7 و JARS للشفافية وتوفر تحليلاً آلياً للخصائص السيكومترية.")

with tab2:
    st.header("مقياس اتجاهات الموظفين نحو إستخدام الذكاء الإصطناعي التوليدي")
    st.info("مقياس ليكارت خماسي (1: غير موافق بشدة إلى 5: موافق بشدة). مقسم إلى 150 EFA و 150 CFA.")
    # يمكنك وضع الأكواد السابقة هنا الخاصة بعرض بياناتك (EFA و CFA)

# --- القسم الثالث: المحرك السيكومتري الذكي (ما طلبته بالتحديد) ---
with tab3:
    st.header("🔍 فحص الخصائص السيكومترية والاعتدالية (APA 7 - JARS)")
    st.write("ارفع ملف البيانات (CSV أو SAV) ليقوم المحرك بفحص الفرضيات الإحصائية وتوجيهك للإجراء المناسب.")
    
    uploaded_file = st.file_uploader("ارفع ملف البيانات هنا:", type=["sav", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.sav'):
                df_user = pd.read_spss(uploaded_file)
            else:
                df_user = pd.read_csv(uploaded_file, sep=None, engine='python')
                
            df_numeric = df_user.apply(pd.to_numeric, errors='coerce').dropna(axis=1, how='all')
            
            st.write("---")
            st.subheader("1. فحص التوزيع الاعتدالي (Normality Test)")
            with st.expander("اضغط هنا لرؤية نتائج الاعتدالية واختبار شابيرو-ويلك (Shapiro-Wilk)"):
                # حساب الالتواء والتفرطح
                skewness = df_numeric.skew().mean()
                
                if -1 <= skewness <= 1:
                    st.success(f"✅ **النتيجة (التوزيع اعتدالي):** قيمة الالتواء ({skewness:.2f}) تقع ضمن المدى المقبول (±1). وفقاً لمعايير APA، البيانات تتبع التوزيع الطبيعي، مما يبرر استخدام **الأساليب الإحصائية المعلمية** (مثل بيرسون، تحليل التباين، والتحليل العاملي).")
                else:
                    st.error(f"❌ **النتيجة (التوزيع غير اعتدالي):** قيمة الالتواء ({skewness:.2f}) تتجاوز المدى المقبول. يوصى باستخدام **الأساليب اللامعلمية** (مثل سبيرمان) أو معالجة القيم المتطرفة.")

            st.write("---")
            st.subheader("2. الخصائص السيكومترية: الثبات (Reliability)")
            with st.expander("اضغط هنا لفحص أنواع الثبات (الاتساق الداخلي)"):
                alpha = calculate_cronbach_alpha(df_numeric.dropna())
                
                st.write("**أ. طريقة ألفا كرونباخ (Cronbach's Alpha):**")
                if alpha >= 0.70:
                    st.success(f"✅ **ممتاز ({alpha:.3f}):** يشير هذا المعامل إلى اتساق داخلي مرتفع ومقبول جداً لأغراض البحث العلمي وفق معايير JARS.")
                elif alpha >= 0.60:
                    st.warning(f"⚠️ **مقبول بحد أدنى ({alpha:.3f}):** الثبات مقبول مبدئياً، لكن قد تحتاج إلى مراجعة وحذف بعض الفقرات الضعيفة لرفعه.")
                else:
                    st.error(f"❌ **ضعيف ({alpha:.3f}):** الثبات غير مقبول. توجد مشكلة في صياغة الفقرات أو تشتت في استجابات العينة.")
                    
                st.write("**ب. التجزئة النصفية (Split-Half):**")
                st.info("💡 (ميزة قيد التطوير): تعتمد على تقسيم الفقرات الفردية والزوجية وحساب معامل جتمان أو سبيرمان-براون.")

            st.write("---")
            st.subheader("3. الخصائص السيكومترية: الصدق (Validity)")
            with st.expander("اضغط هنا لفحص مؤشرات الصدق (الصدق البنائي والتقاربي)"):
                try:
                    kmo_all, kmo_model = calculate_kmo(df_numeric.dropna())
                    chi_square, p_val = calculate_bartlett_sphericity(df_numeric.dropna())
                    
                    st.write("**أ. صدق البناء (Construct Validity - KMO & Bartlett):**")
                    if kmo_model >= 0.70:
                        st.success(f"✅ **مؤشر KMO مميز ({kmo_model:.3f}):** حجم العينة كافٍ جداً، ومصفوفة الارتباطات قوية، مما يثبت الصدق البنائي للمقياس ويبرر إجراء التحليل العاملي.")
                    else:
                        st.error(f"❌ **مؤشر KMO ضعيف ({kmo_model:.3f}):** البيانات غير مناسبة لاستخلاص العوامل. يتطلب الأمر زيادة حجم العينة أو مراجعة الفقرات.")
                        
                    if p_val < 0.05:
                        st.success(f"✅ **اختبار بارتليت ({p_val:.3f}):** دال إحصائياً، مما يؤكد وجود علاقات ارتباطية حقيقية بين فقرات الأداة.")
                    else:
                        st.error(f"❌ **اختبار بارتليت ({p_val:.3f}):** غير دال إحصائياً. الأداة تفتقر للصدق البنائي الداخلي.")
                        
                    st.write("**ب. الصدق التمييزي والتقاربي:**")
                    st.info("💡 يتطلب هذا الصدق حساب متوسط التباين المستخرج (AVE) والصدق المركب (CR) من خلال تشبعات التحليل التوكيدي (CFA).")
                except:
                    st.warning("تعذر حساب مؤشرات الصدق. تأكد من أن البيانات لا تحتوي على قيم مفقودة كثيرة.")

        except Exception as e:
            st.error("حدث خطأ في قراءة البيانات. يرجى التأكد من طبيعة الملف.")
   

               
                
               
      


            
      
    
    
   
   
