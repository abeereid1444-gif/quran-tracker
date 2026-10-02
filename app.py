import streamlit as st
import pandas as pd
import requests

# 1. تهيئة الصفحة
st.set_page_config(
    page_title="تقييم تسميع جزء تبارك",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# بيانات التخزين السحابي (استبدليها ببياناتك من موقع jsonbin.io)
BIN_ID = "6abfa100ac6210605a0c3074"
API_KEY = "$2a$10$FAGxxbVpyqo1XDMWGNvbquczAoxTjWYDaxEMGn2.d1MeGTvP8hkra"

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

# دالة لقراءة البيانات السحابية
def load_data():
    try:
        response = requests.get(f"{URL}/latest", headers=HEADERS)
        if response.status_code == 200:
            records = response.json().get("record", [])
            return pd.DataFrame(records)
    except Exception:
        pass
    return pd.DataFrame(columns=["الطالبة", "السورة", "النوع", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

# دالة لحفظ البيانات السحابية
def save_data(df):
    records = df.to_dict(orient="records")
    requests.put(URL, json=records, headers=HEADERS)

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
                total = memo + tajweed
                new_row = {
                    "الطالبة": st.session_state.selected_student,
                    "السورة": surah,
                    "النوع": eval_type,
                    "الحفظ (/5)": memo,
                    "التجويد (/5)": tajweed,
                    "المجموع (/10)": total
                }
                
                # جلب البيانات الحالية وإضافة الصف الجديد ثم الحفظ سحابياً
                df_current = load_data()
                df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_updated)
                
                st.success("تم رفع التقييم وتخزينه سحابياً بنجاح! ✨")
                st.session_state.step = 1
                st.rerun()
                
        with col_back:
            if st.button("تغيير الطالبة ↩️"):
                st.session_state.step = 1
                st.rerun()

# ---------------- التبويب الثاني: الإحصائيات حسب السورة ----------------
with tab2:
    st.subheader("📊 درجات الطالبات لكل سورة (محدّثة مباشر)")
    
    # قراءة البيانات السحابية المحدثة
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
