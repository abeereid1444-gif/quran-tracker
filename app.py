import streamlit as st
import pandas as pd

# 1. تهيئة الصفحة
st.set_page_config(
    page_title="تقييم تسميع جزء تبارك",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تنسيقات للشاشات والجوال
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    .stSelectbox, .stRadio {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

TABARAK_SURAHS = [
    "سورة الملك", "سورة القلم", "سورة الحاقة", "سورة المعارج", 
    "سورة نوح", "سورة الجن", "سورة المزمل", "سورة المدثر", 
    "سورة القيامة", "سورة الإنسان", "سورة المرسلات"
]

STUDENTS = ["عبير", "اشفاق", "ندى", "منيرة", "في", "صفيه"]

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["الطالبة", "السورة", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

if "step" not in st.session_state:
    st.session_state.step = 1

st.title("📖 تقييم تسميع جزء تبارك")

tab1, tab2 = st.tabs(["📝 إدخال تقييم", "📊 الإحصائيات حسب السورة"])

# ---------------- التبويب الأول: إدخال التقييم ----------------
with tab1:
    if st.session_state.step == 1:
        st.subheader("الخطوة 1: اختيار الطالبة")
        student = st.selectbox("اختر اسم الطالبة:", STUDENTS, key="student_select")
        
        st.write("")
        if st.button("متابعة ➔", type="primary"):
            st.session_state.selected_student = student
            st.session_state.step = 2
            st.rerun()

    elif st.session_state.step == 2:
        st.info(f"المقيّم / الطالبة: **{st.session_state.selected_student}**")
        
        surah = st.selectbox("اختر السورة من جزء تبارك:", TABARAK_SURAHS)
        
        st.write("---")
        st.write("### ⭐️ تقييم الحفظ (من 5):")
        memo = st.radio("درجة الحفظ:", [1, 2, 3, 4, 5], index=4, horizontal=True, key="memo_radio")
        
        st.write("### ⭐️️ تقييم التجويد (من 5):")
        tajweed = st.radio("درجة التجويد:", [1, 2, 3, 4, 5], index=4, horizontal=True, key="tajweed_radio")
        
        st.write("---")
        col_sub, col_back = st.columns([2, 1])
        
        with col_sub:
            if st.button("رفع التقييم 📤", type="primary"):
                total = memo + tajweed
                new_row = {
                    "الطالبة": st.session_state.selected_student,
                    "السورة": surah,
                    "الحفظ (/5)": memo,
                    "التجويد (/5)": tajweed,
                    "المجموع (/10)": total
                }
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                st.success("تم رفع التقييم بنجاح! ✨")
                st.session_state.step = 1
                
        with col_back:
            if st.button("تغيير الطالبة ↩️"):
                st.session_state.step = 1
                st.rerun()

# ---------------- التبويب الثاني: الإحصائيات حسب السورة ----------------
with tab2:
    st.subheader("📊 درجات الطالبات لكل سورة")
    
    df = st.session_state.data
    
    if df.empty:
        st.warning("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        # إنشاء تبويبات داخلية لكل سورة
        surah_tabs = st.tabs(TABARAK_SURAHS)
        
        for idx, surah_name in enumerate(TABARAK_SURAHS):
            with surah_tabs[idx]:
                st.write(f"### 📖 {surah_name}")
                
                # تصفية البيانات الخاصة بالسورة المحددة فقط
                surah_data = df[df["السورة"] == surah_name][["الطالبة", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"]]
                
                if surah_data.empty:
                    st.info("لا توجد تقييمات مسجلة لهذه السورة بعد.")
                else:
                    # عرض الجدول عمودياً بشكل مرتب
                    st.dataframe(surah_data, use_container_width=True, hide_index=True)

        st.write("---")
        # زر لتنزيل كل التقرير كملف إكسل
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تنزيل التقرير الشامل بملف Excel/CSV 📥",
            data=csv,
            file_name="تقرير_تقييم_تسميع_جزء_تبارك.csv",
            mime="text/csv"
        )
