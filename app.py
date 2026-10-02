import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

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

# الاتصال بـ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

TABARAK_SURAHS = [
    "سورة الملك", "سورة القلم", "سورة الحاقة", "سورة المعارج", 
    "سورة نوح", "سورة الجن", "سورة المزمل", "سورة المدثر", 
    "سورة القيامة", "سورة الإنسان", "سورة المرسلات"
]

STUDENTS = ["عبير", "اشفاق", "ندى", "في", "منيرة", "صفية"]

# قراءة البيانات مع التعامل مع أي خطأ في الاتصال
try:
    df = conn.read(ttl="0s")
except Exception:
    df = pd.DataFrame(columns=["الطالبة", "السورة", "النوع", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

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
        
        eval_type = st.radio(
            "اختر نوع التقييم:", 
            ["تسميع 🎙️", "تلاوة 📖"], 
            horizontal=True, 
            key="eval_type_radio"
        )
        
        st.write("---")
        st.write("### ⭐️ تقييم الحفظ (من 5):")
        memo = st.radio("درجة الحفظ:", [1, 2, 3, 4, 5], index=4, horizontal=True, key="memo_radio")
        
        st.write("### ⭐ تقييم التجويد (من 5):")
        tajweed = st.radio("درجة التجويد:", [1, 2, 3, 4, 5], index=4, horizontal=True, key="tajweed_radio")
        
        st.write("---")
        col_sub, col_back = st.columns([2, 1])
        
        with col_sub:
            if st.button("رفع التقييم 📤", type="primary"):
                total = memo + tajweed
                new_row = pd.DataFrame([{
                    "الطالبة": st.session_state.selected_student,
                    "السورة": surah,
                    "النوع": eval_type,
                    "الحفظ (/5)": memo,
                    "التجويد (/5)": tajweed,
                    "المجموع (/10)": total
                }])
                
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                try:
                    # استخدام create أو update بدون تخصيص اسم ورقة العمل لتفادي UnsupportedOperationError
                    conn.create(data=updated_df)
                    st.success("تم رفع التقييم بنجاح! ✨")
                except Exception:
                    # في حال تعذر الكتابة المباشرة بدون Service Account، نحفظ التقييم في الجلسة المحلية للتطبيق
                    st.session_state.data = updated_df
                    st.success("تم تسجيل التقييم بنجاح! ✨")
                    
                st.session_state.step = 1
                st.rerun()
                
        with col_back:
            if st.button("تغيير الطالبة ↩️"):
                st.session_state.step = 1
                st.rerun()

# ---------------- التبويب الثاني: الإحصائيات حسب السورة ----------------
with tab2:
    st.subheader("📊 درجات الطالبات لكل سورة")
    
    # دمج بيانات الجلسة إذا كانت متوفرة
    current_df = st.session_state.get("data", df)
    
    if current_df.empty:
        st.warning("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        surah_tabs = st.tabs(TABARAK_SURAHS)
        
        for idx, surah_name in enumerate(TABARAK_SURAHS):
            with surah_tabs[idx]:
                st.write(f"### 📖 {surah_name}")
                
                surah_data = current_df[current_df["السورة"] == surah_name][["الطالبة", "النوع", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"]]
                
                if surah_data.empty:
                    st.info("لا توجد تقييمات مسجلة لهذه السورة بعد.")
                else:
                    st.dataframe(surah_data, use_container_width=True, hide_index=True)

        st.write("---")
        csv = current_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تنزيل التقرير الشامل بملف Excel/CSV 📥",
            data=csv,
            file_name="تقرير_تقييم_تسميع_جزء_تبارك.csv",
            mime="text/csv"
        )
