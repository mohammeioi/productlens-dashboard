import streamlit as st
import pandas as pd
from rembg import remove
from PIL import Image
import io
import base64

# إعدادات الصفحة
st.set_page_config(page_title="مدير المنتجات الذكي", layout="wide")

# تهيئة مخزن البيانات وحقول الإدخال الافتراضية
if 'product_list' not in st.session_state:
    st.session_state.product_list = []
if 'categories' not in st.session_state:
    st.session_state.categories = ["عام"]
if 'temp_url' not in st.session_state:
    st.session_state.temp_url = ""
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# مفاتيح حقول ال��دخال لتسهيل الملء التلقائي عند التعديل
if 'input_name' not in st.session_state:
    st.session_state.input_name = ""
if 'input_price' not in st.session_state:
    st.session_state.input_price = 0
if 'input_category' not in st.session_state:
    st.session_state.input_category = st.session_state.categories[0]
if 'input_image_url' not in st.session_state:
    st.session_state.input_image_url = st.session_state.temp_url

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
            st.session_state.input_image_url = fake_url
            
            with col2:
                st.image(output_image, caption="الصورة المعالجة", width=250)
                st.success("تمت المعالجة!")

st.markdown("---")

# القسم الثاني: إدخال البيانات (نستخدم مفاتيح session_state للحقول)
st.header("2. تفاصيل المنتج")
col_a, col_b, col_c = st.columns(3)

with col_a:
    name = st.text_input("اسم المنتج", value=st.session_state.input_name, key="input_name")

with col_b:
    price = st.number_input("السعر", min_value=0, step=250, format="%d", value=st.session_state.input_price, key="input_price")

with col_c:
    # نعرض الفئات، ونحافظ على القيمة في input_category
    category_option = st.selectbox("اختر الفئة", options=st.session_state.categories + ["+ إضافة فئة جديدة"], index=st.session_state.categories.index(st.session_state.input_category) if st.session_state.input_category in st.session_state.categories else 0)
    st.session_state.input_category = category_option
    if category_option == "+ إضافة فئة جديدة":
        new_cat = st.text_input("اكتب اسم الفئة الجديدة")
        if st.button("حفظ الفئة"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat)
                st.session_state.input_category = new_cat
                st.rerun()

image_url = st.text_input("رابط الصورة", value=st.session_state.input_image_url, key="input_image_url")

# زر إضافة أو تعديل
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("إضافة المنتج للقائمة"):
        if name and image_url:
            if st.session_state.edit_index is not None:
                # تعديل منتج موجود (نحتفظ بالرابط تحت المفتاح 'الصورة')
                st.session_state.product_list[st.session_state.edit_index] = {
                    "الاسم": name,
                    "السعر": price,
                    "الفئة": category_option,
                    "الصورة": image_url
                }
                st.session_state.edit_index = None
                st.success("تم تعديل المنتج!")
            else:
                # إضافة منتج جديد
                new_product = {
                    "الاسم": name,
                    "السعر": price,
                    "الفئة": category_option,
                    "الصورة": image_url
                }
                st.session_state.product_list.append(new_product)
                st.success("تمت إضافة المنتج!")
            # إعادة تهيئة حقول الإدخال بعد الإضافة/التعديل
            st.session_state.input_name = ""
            st.session_state.input_price = 0
            st.session_state.input_category = st.session_state.categories[0]
            st.session_state.input_image_url = ""
            st.session_state.temp_url = ""
            st.rerun()
        else:
            st.error("يرجى إكمال البيانات.")

with col_btn2:
    if st.session_state.edit_index is not None:
        if st.button("إلغاء التعديل"):
            st.session_state.edit_index = None
            # إعادة تهيئة الحقول
            st.session_state.input_name = ""
            st.session_state.input_price = 0
            st.session_state.input_category = st.session_state.categories[0]
            st.session_state.input_image_url = ""
            st.rerun()

st.markdown("---")

# القسم الثالث: الجدول والتصدير
st.header("3. قائمة المنتجات")
if st.session_state.product_list:
    # نجهز نسخة للعرض حيث نُظهر في عمود الصورة كلمة ثابتة "الصورة"
    df = pd.DataFrame(st.session_state.product_list)
    df_display = df.copy()
    if "الصورة" in df_display.columns:
        df_display["الصورة"] = "الصورة"  # كل الخلايا تعرض الكلمة المفردة المطلوبة

    st.table(df_display)

    # أزرار التعديل والحذف لكل صف (نستخدم حفظ قيم المنتج في session_state عند الضغط)
    st.subheader("إدارة المنتجات")
    for idx, product in enumerate(st.session_state.product_list):
        cols = st.columns([2, 1, 1, 1, 1])  # عرض اسم + أزرار
        cols[0].markdown(f"**{product['الاسم']}**")
        # عرض زر لفتح الصورة في تبويب جديد (ينقلك للرابط الفعلي)
        if cols[1].button("عرض الصورة", key=f"view_{idx}"):
            # نستخدم markdown لفتح الرابط (المستخدم يمكن النقر لفتح)
            st.markdown(f"[فتح الصورة]({product.get('الصورة','')})")
        if cols[2].button("✏️ تعديل", key=f"edit_{idx}"):
            # تعبئة الحقول بالبيانات الحالية ثم إعادة تشغيل لعرضها في الحقول
            st.session_state.edit_index = idx
            st.session_state.input_name = product.get("الاسم", "")
            st.session_state.input_price = product.get("السعر", 0)
            st.session_state.input_category = product.get("الفئة", st.session_state.categories[0])
            st.session_state.input_image_url = product.get("الصورة", "")
            st.rerun()
        if cols[3].button("🗑️ حذف", key=f"delete_{idx}"):
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
