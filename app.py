import streamlit as st
import pandas as pd
import os

# 1. إعدادات الشاشة لتناسب الجوال بالكامل
st.set_page_config(
    page_title="تطبيق تقييم التسميع",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"  # إخفاء القائمة الجانبية تلقائيًا على الجوال
)

# تحسين مظهر الواجهة للجوال عبر CSS بسيط
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px !important;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ملف حفظ البيانات المحلي
DATA_FILE = "evaluations.csv"

if os.path.exists(DATA_FILE):
    df_saved = pd.read_csv(DATA_FILE)
else:
    df_saved = pd.DataFrame(columns=["تاريخ التقييم", "اسم الطالبة المقيِّمة", "اسم الطالبة الشريكة", "السورة", "تقييم الحفظ (/5)", "تقييم التجويد (/5)", "المجموع (/10)", "الملاحظات"])

if "data" not in st.session_state:
    st.session_state.data = df_saved

# قائمة سور جزء تبارك
SURAH_LIST = [
    "سورة الملك (تبارك)",
    "سورة القلم",
    "سورة الحاقة",
    "سورة المعارج",
    "سورة نوح",
    "سورة الجن",
    "سورة المزمل",
    "سورة المدثر",
    "سورة القيامة",
    "سورة الإنسان",
    "سورة المرسلات"
]

# 3. التنقل بين الصفحات أسفل الشاشة أو في القائمة
st.sidebar.title("📌 التنقل")
page = st.sidebar.radio("اختر الصفحة:", ["إدخال تقييم جديد 📝", "الإحصائيات والتقارير 📊"])

# ---------------- الصفحة الأولى: تسجيل التقييم ----------------
if page == "إدخال تقييم جديد 📝":
    st.title("📝 تقييم تسميع جزء تبارك")
    st.caption("برجاء تعبئة البيانات التالية بدقة:")
    
    # كتابة أسماء الطالبات حرًا
    student_evaluator = st.text_input("اسم الطالبة (المقيِّمة):", placeholder="أكتبي اسمك هنا...")
    student_partner = st.text_input("اسم الطالبة (الشريكة):", placeholder="أكتبي اسم شريكتك هنا...")
    
    surah_selected = st.selectbox("اختر السورة المراد تقييمها:", SURAH_LIST)
    
    st.write("---")
    st.subheader("⭐ درجات التقييم")
    
    memo_score = st.slider("تقييم الحفظ (من 5):", 1, 5, 5)
    tajweed_score = st.slider("تقييم التجويد (من 5):", 1, 5, 5)
    
    notes = st.text_area("ملاحظات إضافية (اختياري):", placeholder="أكتبي أي ملاحظات عن التسميع...")
    
    if st.button("رفع التقييم 📤"):
        if not student_evaluator.strip() or not student_partner.strip():
            st.error("⚠️ يرجى كتابة اسم الطالبة المقيِّمة والشريكة قبل الرفع!")
        else:
            total = memo_score + tajweed_score
            today_date = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            
            new_entry = {
                "تاريخ التقييم": today_date,
                "اسم الطالبة المقيِّمة": student_evaluator.strip(),
                "اسم الطالبة الشريكة": student_partner.strip(),
                "السورة": surah_selected,
                "تقييم الحفظ (/5)": memo_score,
                "تقييم التجويد (/5)": tajweed_score,
                "المجموع (/10)": total,
                "الملاحظات": notes
            }
            
            # إضافة السجل للجدول وحفظه في الملف
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_entry])], ignore_index=True)
            st.session_state.data.to_csv(DATA_FILE, index=False)
            
            st.success(f"تم رفع تقييم سورة ({surah_selected}) بنجاح! ✨")

# ---------------- الصفحة الثانية: الإحصائيات ----------------
elif page == "الإحصائيات والتقارير 📊":
    st.title("📊 برنت البيانات والإحصائيات")
    
    df = st.session_state.data
    
    if df.empty:
        st.info("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        # ملخص سريع
        col1, col2 = st.columns(2)
        col1.metric("إجمالي التقييمات", len(df))
        col2.metric("متوسط التقدير العام", f"{df['المجموع (/10)'].mean():.1f} / 10")
        
        st.write("---")
        st.write("### 📋 سجل التقييمات الملون:")
        
        # عرض البيانات بتنسيق ملون ومتناسب مع الجوال
        st.dataframe(
            df.style.background_gradient(subset=["المجموع (/10)"], cmap="Greens"),
            use_container_width=True
        )
        
        # زر لتحميل البيانات كملف Excel/CSV
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تحميل برنت التقييمات (CSV) 📥",
            data=csv_data,
            file_name="تقارير_تسميع_تبارك.csv",
            mime="text/csv"
        )
