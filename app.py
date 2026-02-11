import streamlit as st
import pandas as pd
from rembg import remove
from PIL import Image
import io

# 1. إعدادات الصفحة
st.set_page_config(page_title="مدير المنتجات - تخصيص كامل", layout="wide")

# 2. تهيئة مخزن البيانات
if 'product_list' not in st.session_state:
    st.session_state.product_list = []
if 'columns' not in st.session_state:
    # الأعمدة الافتراضية التي يمكنك حذفها أو تغييرها من الواجهة
    st.session_state.columns = ["الاسم", "السعر", "الفئة", "الصورة"]
if 'temp_url' not in st.session_state:
    st.session_state.temp_url = ""

st.title("⚙️ نظام إدارة المنتجات (تحكم كامل بالحقول)")

# --- القسم الجديد: إعدادات الحقول ---
with st.expander("🛠️ إعدادات الحقول والأعمدة (أضف/احذف/عدل الحقول الأساسية)"):
    st.write("صمم شكل الجدول الخاص بك هنا:")
    
    # إضافة حقل جديد
    new_col = st.text_input("اسم الحقل الجديد")
    if st.button("إضافة حقل"):
        if new_col and new_col not in st.session_state.columns:
            st.session_state.columns.append(new_col)
            st.rerun()
            
    # عرض الحقول الحالية مع خيار الحذف
    st.write("الحقول الحالية:")
    cols_to_delete = []
    for c in st.session_state.columns:
        c1, c2 = st.columns([4, 1])
        c1.text(f"📍 {c}")
        if c2.button("حذف", key=f"del_col_{c}"):
            st.session_state.columns.remove(c)
            st.rerun()

st.markdown("---")

# القسم الأول: معالجة الصورة (اختياري)
st.header("1. معالجة صورة المنتج")
uploaded_file = st.file_uploader("اختر صورة المنتج...", type=["jpg", "jpeg", "png"])
if uploaded_file:
    if st.button("حذف الخلفية"):
        with st.spinner("جاري المعالجة..."):
            img = remove(Image.open(uploaded_file))
            st.session_state.temp_url = f"https://img-host.com/img_{len(st.session_state.product_list)}.png"
            st.image(img, width=200)
            st.success("تمت المعالجة!")

st.markdown("---")

# القسم الثاني: إدخال البيانات حسب الحقول المختارة
st.header("2. إدخال بيانات المنتج")
new_entry = {}

# توليد حقول الإدخال ديناميكياً بناءً على قائمة الأعمدة
grid_cols = st.columns(len(st.session_state.columns) if st.session_state.columns else 1)

for i, col_name in enumerate(st.session_state.columns):
    with grid_cols[i % len(grid_cols)]:
        if "السعر" in col_name:
            new_entry[col_name] = st.number_input(col_name, min_value=0, format="%d", key=f"input_{col_name}")
        elif "الصورة" in col_name:
            new_entry[col_name] = st.text_input(col_name, value=st.session_state.temp_url, key=f"input_{col_name}")
        else:
            new_entry[col_name] = st.text_input(col_name, key=f"input_{col_name}")

if st.button("➕ إضافة المنتج للقائمة"):
    if any(new_entry.values()):
        st.session_state.product_list.append(new_entry)
        st.session_state.temp_url = ""
        st.success("تمت الإضافة!")
        st.rerun()

st.markdown("---")

# القسم الثالث: الإدارة والتصدير
st.header("3. إدارة القائمة")
if st.session_state.product_list:
    df = pd.DataFrame(st.session_state.product_list)
    
    # التأكد من ترتيب الأعمدة حسب اختيار المستخدم
    df = df.reindex(columns=st.session_state.columns)
    
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "السعر": st.column_config.NumberColumn(format="%d"),
            "الصورة": st.column_config.LinkColumn()
        }
    )
    
    if st.button("💾 حفظ كل التغييرات"):
        st.session_state.product_list = edited_df.to_dict('records')
        st.success("تم الحفظ!")
    
    # تصدير Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_df.to_excel(writer, index=False)
    st.download_button("📥 تحميل Excel", output.getvalue(), "products.xlsx")
else:
    st.info("القائمة فارغة.")