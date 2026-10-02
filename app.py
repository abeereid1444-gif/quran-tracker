import streamlit as st
import pandas as pd

# إعداد الصفحة
st.set_page_config(page_title="تطبيق تقييم التسميع", page_icon="📖", layout="centered")

# القائمة الجانبية للتنقل
st.sidebar.title("📌 القائمة")
page = st.sidebar.radio("اختر الصفحة:", ["إدخال تقييم جديد 📝", "الإحصائيات والتقارير 📊"])

STUDENTS = ["طالبة 1", "طالبة 2", "طالبة 3", "طالبة 4", "طالبة 5", "طالبة 6"]
SURAHS = ["سورة الإنسان", "سورة المدثر", "سورة المزمل", "سورة الجن"]

# تهيئة مخزن البيانات في الجلسة
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["الطالبة", "السورة", "الحفظ (/5)", "التجويد (/5)", "المجموع (/10)"])

# ---------------- الصفحة الأولى: إدخال التقييم ----------------
if page == "إدخال تقييم جديد 📝":
    st.title("📝 إدخال تقييم التسميع")
    
    student = st.selectbox("اختر اسم الطالبة:", STUDENTS)
    
    if st.button("متابعة ➔"):
        st.session_state.selected_student = student
        st.session_state.step = 2

    if st.session_state.get("step") == 2:
        st.write("---")
        st.write(f"المقيِّم/الطالبة: **{st.session_state.selected_student}**")
        surah = st.selectbox("اختر السورة:", SURAHS)
        
        memo = st.slider("تقييم الحفظ:", 1, 5, 5)
        tajweed = st.slider("تقييم التجويد:", 1, 5, 5)
        
        if st.button("رفع التقييم 📤"):
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

# ---------------- الصفحة الثانية: الإحصائيات ----------------
elif page == "الإحصائيات والتقارير 📊":
    st.title("📊 برنت وإحصائيات التقييمات")
    
    df = st.session_state.data
    
    if df.empty:
        st.warning("لا توجد بيانات مسجلة حاليًا.")
    else:
        # كروت ملونة سريعة
        col1, col2 = st.columns(2)
        col1.metric("عدد التقييمات", len(df))
        col2.metric("متوسط التقدير العام", f"{df['المجموع (/10)'].mean():.1f} / 10")
        
        st.write("### 📋 جدول البيانات الملون والمرتب:")
        # تلوين الدرجات بالأخضر والتدريج لسهولة القراءة
        st.dataframe(
            df.style.background_gradient(subset=["المجموع (/10)"], cmap="Greens")
        )
