import streamlit as st
import pandas as pd

# 1. تهيئة الصفحة لتناسب الجوال بالكامل
st.set_page_config(
    page_title="تقييم تسميع جزء تبارك",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# تحسين تنسيق CSS للشاشات الصغيرة والأزرار
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

# قائمة سور جزء تبارك كاملة
TABARAK_SURAHS = [
    "سورة الملك", "سورة القلم", "سورة الحاقة", "سورة المعارج", 
    "سورة نوح", "سورة الجن", "سورة المزمل", "سورة المدثر", 
    "سورة القيامة", "سورة الإنسان", "سورة المرسلات"
]

STUDENTS = ["طالبة 1", "طالبة 2", "طالبة 3", "طالبة 4", "طالبة 5", "طالبة 6"]

# مخزن البيانات في الجلسة
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["الطالبة", "السورة", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

if "step" not in st.session_state:
    st.session_state.step = 1

st.title("📖 تقييم تسميع جزء تبارك")

# تبويبات متوافقة مع شاشة الجوال
tab1, tab2 = st.tabs(["📝 إدخال تقييم", "📊 الإحصائيات والبرنت"])

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
        
        st.write("### ⭐️ تقييم التجويد (من 5):")
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

# ---------------- التبويب الثاني: الإحصائيات ----------------
with tab2:
    st.subheader("📊 برنت البيانات والتقارير")
    
    df = st.session_state.data
    
    if df.empty:
        st.warning("لا توجد تقييمات مسجلة حتى الآن.")
    else:
        # كروت ملونة سريعة للشاشة
        col1, col2 = st.columns(2)
        col1.metric("إجمالي التقييمات", len(df))
        col2.metric("متوسط التقدير العام", f"{df['المجموع (/10)'].mean():.1f} / 10")
        
        st.write("### 📋 جدول السجلات الملون:")
        st.dataframe(
            df.style.background_gradient(subset=["المجموع (/10)"], cmap="Greens"),
            use_container_width=True
        )
        
        # زر لتنزيل البيانات للطباعة/إكسل
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="تنزيل التقرير بملف Excel/CSV 📥",
            data=csv,
            file_name="تقرير_تقييم_تسميع_جزء_تبارك.csv",
            mime="text/csv"
        )
