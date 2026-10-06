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

# مفاتيح الاتصال الخاصة بك
BIN_ID = "6abfa100ac6210605a0c3074"
API_KEY = "$2a$10$FAGxxbVpyqo1XDMWGNvbquczAoxTjWYDaxEMGn2.d1MeGTvP8hkra"

URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": API_KEY
}

# دالة مأمونة لجلب البيانات مع ذاكرة مؤقتة لمنع التعليق
@st.cache_data(ttl=5)
def load_data():
    try:
        res = requests.get(f"{URL}/latest", headers=HEADERS, timeout=5)
        if res.status_code == 200:
            data = res.json().get("record", {})
            records = data.get("records", []) if isinstance(data, dict) else []
            df = pd.DataFrame(records)
            if not df.empty and "الجزئية" not in df.columns:
                df["الجزئية"] = "غير محدد"
            return df
    except Exception:
        pass
    return pd.DataFrame(columns=["الطالبة", "السورة", "النوع", "الجزئية", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

# دالة مأمونة لحفظ البيانات وتحديث التخزين المؤقت
def save_data(df):
    try:
        clean_df = df.copy()
        clean_df["الحفظ (/5)"] = clean_df["الحفظ (/5)"].astype(int)
        clean_df["التجويد (/5)"] = clean_df["التجويد (/5)"].astype(int)
        clean_df["المجموع (/10)"] = clean_df["المجموع (/10)"].astype(int)
        
        records = clean_df.to_dict(orient="records")
        payload = {"records": records}
        
        res = requests.put(URL, json=payload, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            st.cache_data.clear()
            return True
    except Exception:
        pass
    return False

# نفس القائمة الخاصة بك بدون أي تغيير
TABARAK_SURAHS = [
    "سورة الملك", "سورة القلم", "سورة الحاقة", "سورة المعارج", 
    "سورة نوح", "سورة الجن", "سورة المزمل", "سورة المدثر", 
    "سورة القيامة", "سورة الإنسان", "جزء النباء"
]

STUDENTS = ["عبير", "اشفاق", "ندى", "في", "منيرة", "ايناس", "صفية"]

st.title("📖 تقييم تسميع جزء تبارك")

tab1, tab2 = st.tabs(["📝 إدخال تقييم", "📊 الإحصائيات حسب السورة"])

# ---------------- التبويب الأول: إدخال التقييم ----------------
with tab1:
    student = st.selectbox("اختر اسم الطالبة:", STUDENTS, key="student_select")
    surah = st.selectbox("اختر السورة من جزء تبارك:", TABARAK_SURAHS, key="surah_select")
    
    eval_type = st.radio(
        "اختر نوع التقييم:", 
        ["تسميع 🎙", "تلاوة 📖"], 
        horizontal=True, 
        key="eval_type_radio"
    )
    
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
    if st.button("رفع التقييم 📤", type="primary"):
        total = int(memo) + int(tajweed)
        new_row = {
            "الطالبة": str(student),
            "السورة": str(surah),
            "النوع": str(eval_type),
            "الجزئية": str(part_section).replace(" 📍", ""),
            "الحفظ (/5)": int(memo),
            "التجويد (/5)": int(tajweed),
            "المجموع (/10)": int(total)
        }
        
        with st.spinner("جاري التخزين السحابي..."):
            df_current = load_data()
            df_updated = pd.concat([df_current, pd.DataFrame([new_row])], ignore_index=True)
            
            if save_data(df_updated):
                st.success(f"تم رفع تقييم الطالبة ({student}) لـ ({surah}) بنجاح! ✨")
            else:
                st.error("فشل الحفظ، يرجى إعادة المحاولة.")

# ---------------- التبويب الثاني: الإحصائيات حسب السورة ----------------
with tab2:
    df = load_data()
    
    if df.empty:
        st.warning("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        # 1. تفاصيل درجات الطالبات لكل سورة أولاً
        st.subheader("📊 تفاصيل درجات الطالبات لكل سورة")
        
        surah_tabs = st.tabs(TABARAK_SURAHS)
        
        for idx, surah_name in enumerate(TABARAK_SURAHS):
            with surah_tabs[idx]:
                st.write(f"### 📖 {surah_name}")
                
                columns_to_show = ["الطالبة", "النوع", "الجزئية", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"]
                available_cols = [c for c in columns_to_show if c in df.columns]
                
                surah_data = df[df["السورة"] == surah_name][available_cols]
                
                if surah_data.empty:
                    st.info("لا توجد تقييمات مسجلة لهذه السورة بعد.")
                else:
                    st.dataframe(surah_data, use_container_width=True, hide_index=True)

        st.write("---")
        
        # 2. جدول ملخص عدد مرات التسميع لكل طالبة ثانياً
        st.subheader("📈 ملخص عدد مرات التسميع لكل طالبة")
        
        summary_df = df.pivot_table(
            index="الطالبة", 
            columns="السورة", 
            aggfunc="size", 
            fill_value=0
        )
        
        summary_df = summary_df.reindex(index=STUDENTS, columns=TABARAK_SURAHS, fill_value=0)
        summary_display = summary_df.astype(int)
        
        st.dataframe(summary_display, use_container_width=True)

        st.write("---")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تنزيل التقرير الشامل بملف Excel/CSV 📥",
            data=csv,
            file_name="تقرير_تقييم_تسميع_جزء_تبارك.csv",
            mime="text/csv"
        )
