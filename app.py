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

# ضعِي بياناتك الحقيقية هنا
BIN_ID = "ضعِي_هنا_BIN_ID"
API_KEY = "ضعِي_هنا_SECRET_KEY"

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

# دالة مأمونة لجلب البيانات
def load_data():
    try:
        res = requests.get(f"{URL}/latest", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json().get("record", {})
            records = data.get("records", []) if isinstance(data, dict) else []
            df = pd.DataFrame(records)
            # التأكد من وجود عمود "الجزئية" حتى للسجلات القديمة
            if not df.empty and "الجزئية" not in df.columns:
                df["الجزئية"] = "غير محدد"
            return df
        else:
            st.error(f"تنبيه السحابة: رمز {res.status_code}")
    except Exception as e:
        st.error(f"خطأ اتصالات: {e}")
    return pd.DataFrame(columns=["الطالبة", "السورة", "النوع", "الجزئية", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

# دالة مأمونة لحفظ البيانات
def save_data(df):
    try:
        clean_df = df.copy()
        clean_df["الحفظ (/5)"] = clean_df["الحفظ (/5)"].astype(int)
        clean_df["التجويد (/5)"] = clean_df["التجويد (/5)"].astype(int)
        clean_df["المجموع (/10)"] = clean_df["المجموع (/10)"].astype(int)
        
        records = clean_df.to_dict(orient="records")
        payload = {"records": records}
        
        res = requests.put(URL, json=payload, headers=HEADERS, timeout=10)
        return res.status_code == 200
    except Exception as e:
        st.error(f"خطأ بالحفظ: {e}")
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
        
        # اختيار نوع التقييم
        eval_type = st.radio(
            "اختر نوع التقييم:", 
            ["تسميع 🎙", "تلاوة 📖"], 
            horizontal=True, 
            key="eval_type_radio"
        )
        
        # اختيار الجزئية (3 خانات أفقية جنبًا إلى جنب)
        part_section = st.radio(
            "اختر الجزئية المطلوب تقييمها:", 
            ["الجزئية الأولى 📍", "الجزئية الثانية 📍", "الجزئية الأخيرة 📍"], 
            horizontal=True, 
            key="part_section_radio"
        )
        
        st.write("---")
        st.write("### ⭐ تقييم الحفظ (من 5):")
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
                    "الجزئية": str(part_section).replace(" 📍", ""),
                    "الحفظ (/5)": int(memo),
                    "التجويد (/5)": int(tajweed),
                    "المجموع (/10)": int(total)
                }
                
                df_current = load_data()
                df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
                
                if save_data(df_updated):
                    st.success("تم رفع التقييم وتخزينه سحابياً بنجاح! ✨")
                    st.session_state.step = 1
                    st.rerun()
                else:
                    st.error("فشل الحفظ، يرجى التأكد من المفاتيح.")
                
        with col_back:
            if st.button("تغيير الطالبة ↩️️"):
                st.session_state.step = 1
                st.rerun()

# ---------------- التبويب الثاني: الإحصائيات حسب السورة ----------------
with tab2:
    st.subheader("📊 درجات الطالبات لكل سورة")
    
    df = load_data()
    
    if df.empty:
        st.warning("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        surah_tabs = st.tabs(TABARAK_SURAHS)
        
        for idx, surah_name in enumerate(TABARAK_SURAHS):
            with surah_tabs[idx]:
                st.write(f"### 📖 {surah_name}")
                
                # إظهار أعمدة الجدول متضمنة عمود الجزئية
                columns_to_show = ["الطالبة", "النوع", "الجزئية", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"]
                available_cols = [c for c in columns_to_show if c in df.columns]
                
                surah_data = df[df["السورة"] == surah_name][available_cols]
                
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
