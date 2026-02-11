import streamlit as st
import pandas as pd
from rembg import remove
from PIL import Image
import io
import base64

# إعدادات الصفحة
st.set_page_config(page_title="مدير المنتجات الذكي", layout="wide")

# تهيئة مخزن البيانات
if 'product_list' not in st.session_state:
    st.session_state.product_list = []
if 'categories' not in st.session_state:
    st.session_state.categories = ["عام"]
if 'temp_url' not in st.session_state:
    st.session_state.temp_url = ""

st.title("📦 نظام إضافة المنتجات مع معالجة الصور")
st.markdown("---")

# القسم الأول: معالجة الصورة
st.header("1. معالجة صورة المنتج")
uploaded_file = st.file_uploader("اختر صورة المنتج...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="الصورة الأصلية", width=250)
    
    if st.button("ضغط الصورة وحذف الخلفية"):
        with st.spinner("جاري المعالجة... (قد تستغرق دقيقة في المرة الأولى)"):
            input_image = Image.open(uploaded_file)
            output_image = remove(input_image)
            
            # محاكاة رابط (يمكنك تطويرها لاحقاً لرفع حقيقي)
            fake_url = f"https://img-host.com/product_{len(st.session_state.product_list)}.png"
            st.session_state.temp_url = fake_url
            
            with col2:
                st.image(output_image, caption="الصورة المعالجة", width=250)
                st.success("تمت المعالجة!")

st.markdown("---")

# القسم الثاني: إدخال البيانات
st.header("2. تفاصيل المنتج")
col_a, col_b, col_c = st.columns(3)

with col_a:
    name = st.text_input("اسم المنتج")
    
with col_b:
    # تعديل السعر ليظهر كعدد صحيح (بدون أصفار زائدة)
    price = st.number_input("السعر", min_value=0, step=250, format="%d")

with col_c:
    category_option = st.selectbox("اختر الفئة", options=st.session_state.categories + ["+ إضافة فئة جديدة"])
    category = category_option
    if category_option == "+ إضافة فئة جديدة":
        new_cat = st.text_input("اكتب اسم الفئة الجديدة")
        if st.button("حفظ الفئة"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat)
                st.rerun()

image_url = st.text_input("رابط الصورة", value=st.session_state.temp_url)

if st.button("إضافة المنتج للقائمة"):
    if name and image_url:
        new_product = {
            "الاسم": name,
            "السعر": price,
            "الفئة": category,
            "رابط الصورة": image_url
        }
        st.session_state.product_list.append(new_product)
        st.session_state.temp_url = "" 
        st.success("تمت إضافة المنتج!")
    else:
        st.error("يرجى إكمال البيانات.")

st.markdown("---")

# القسم الثالث: الجدول والتصدير
st.header("3. قائمة المنتجات")
if st.session_state.product_list:
    df = pd.DataFrame(st.session_state.product_list)
    st.table(df)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 تحميل الجدول (Excel)",
        data=output.getvalue(),
        file_name="products.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )