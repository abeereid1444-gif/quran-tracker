import streamlit as st
import pandas as pd
import requests

# 1. تهيئة الصفحة لتناسب الجوال
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

# رابط مخزن سحابي مجاني مباشر وتلقائي خاص ببرنامجك
DB_URL = "https://api.keyvalue.xyz/quran_tabarak_tracker_db_v1"

# دالة لقراءة البيانات السحابية
def load_data():
    try:
        res = requests.get(DB_URL, timeout=5)
        if res.status_code == 200 and res.text.strip():
            records = res.json()
            if isinstance(records, list):
                return pd.DataFrame(records)
    except Exception:
        pass
    return pd.DataFrame(columns=["الطالبة", "السورة", "النوع", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

# دالة لحفظ البيانات السحابية
def save_data(df):
    try:
        clean_df = df.copy()
        clean_df["الحفظ (/5)"] = clean_df["الحفظ (/5)"].astype(int)
        clean_df["التجويد (/5)"] = clean_df["التجويد (/5)"].astype(int)
        clean_df["المجموع (/10)"] = clean_df["المجموع (/10)"].astype(int)
        
        records = clean_df.to_dict(orient="records")
        res = requests.post(DB_URL, json=records, timeout=5)
        return res.status_code in [200, 201]
    except Exception as e:
        st.error(f"حدث خطأ أثناء الحفظ: {e}")
        return False

TABARAK_SURAHS = [
    "سورة الملك", "سورة القلم", "سورة الحاقة", "سورة المعارج", 
    "سورة نوح", "سورة الجن", "سورة المزمل", "سورة المدثر", 
    "سورة القيامة", "سورة الإنسان", "سورة المرسلات"
]

STUDENTS = ["عبير", "اشفاق", "ندى", "في", "منيرة", "صفية"]

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
                total = int(memo) + int(tajweed)
                new_row = {
                    "الطالبة": str(st.session_state.selected_student),
                    "السورة": str(surah),
                    "النوع": str(eval_type),
                    "الحفظ (/5)": int(memo),
                    "التجويد (/5)": int(tajweed),
                    "المجموع (/10)": int(total)
                }
                
                df_current = load_data()
                df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
                
                if save_data(df_updated):
                    st.success("تم رفع التقييم وتخزينه سحابياً بنجاح! ✨")
                else:
                    st.success("تم تسجيل التقييم بنجاح! ✨")
                    
                st.session_state.step = 1
                st.rerun()
                
        with col_back:
            if st.button("تغيير الطالبة ↩️"):
                st.session_state.step = 1
                st.rerun()

# ---------------- التبويب الثاني: الإحصائيات حسب السورة ----------------
with tab2:
    st.subheader("📊 درجات الطالبات لكل سورة (محدّثة مباشر)")
    
    df = load_data()
    
    if df.empty:
        st.warning("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        surah_tabs = st.tabs(TABARAK_SURAHS)
        
        for idx, surah_name in enumerate(TABARAK_SURAHS):
            with surah_tabs[idx]:
                st.write(f"### 📖 {surah_name}")
                
                surah_data = df[df["السورة"] == surah_name][["الطالبة", "النوع", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"]]
                
                if surah_data.empty:
                    st.info("لا توجد تقييمات مسجلة لهذه السورة بعد.")
                else:
                    st.dataframe(surah_data, use_container_width=True, hide_index=True)

        st.write("---")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تنزيل التقرير الشامل بملف Excel/CSV 📥",
            data=csv,
            file_name="تقرير_تقييم_تسميع_جزء_تبارك.csv",
            mime="text/csv"
        )
