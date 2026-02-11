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
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

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

# زر إضافة أو تعديل
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("إضافة المنتج للقائمة"):
        if name and image_url:
            if st.session_state.edit_index is not None:
                # تعديل منتج موجود
                st.session_state.product_list[st.session_state.edit_index] = {
                    "الاسم": name,
                    "السعر": price,
                    "الفئة": category,
                    "الصور": image_url
                }
                st.session_state.edit_index = None
                st.success("تم تعديل المنتج!")
            else:
                # إضافة منتج جديد
                new_product = {
                    "الاسم": name,
                    "السعر": price,
                    "الفئة": category,
                    "الصور": image_url
                }
                st.session_state.product_list.append(new_product)
                st.success("تمت إضافة المنتج!")
            st.session_state.temp_url = ""
            st.rerun()
        else:
            st.error("يرجى إكمال البيانات.")

with col_btn2:
    if st.session_state.edit_index is not None:
        if st.button("إلغاء التعديل"):
            st.session_state.edit_index = None
            st.rerun()

st.markdown("---")

# القسم الثالث: الجدول والتصدير
st.header("3. قائمة المنتجات")
if st.session_state.product_list:
    df = pd.DataFrame(st.session_state.product_list)
    st.table(df)
    
    # أزرار التعديل والحذف
    st.subheader("إدارة المنتجات")
    col1, col2, col3, col4 = st.columns(4)
    
    for idx, product in enumerate(st.session_state.product_list):
        with col1 if idx % 4 == 0 else (col2 if idx % 4 == 1 else (col3 if idx % 4 == 2 else col4)):
            st.write(f"**{product['الاسم']}**")
            
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button(f"✏️ تعديل", key=f"edit_{idx}"):
                    # حشو الحقول بقيم المنتج للاستخدام في التعديل
                    st.session_state.edit_index = idx
                    st.experimental_set_query_params()  # يجبر rerun آمن
                    st.session_state.show_fill = True
                    st.session_state.fill_name = product["الاسم"]
                    st.session_state.fill_price = product["السعر"]
                    st.session_state.fill_category = product["الفئة"]
                    st.session_state.fill_image_url = product["الصور"]
                    st.rerun()
            
            with col_delete:
                if st.button(f"🗑️ حذف", key=f"delete_{idx}"):
                    st.session_state.product_list.pop(idx)
                    st.success("تم حذف المنتج!")
                    st.rerun()
    
    st.markdown("---")
    
    # تصدير إلى Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 تحميل الجدول (Excel)",
        data=output.getvalue(),
        file_name="products.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("لا توجد منتجات حتى الآن. أضف منتج جديد!")
