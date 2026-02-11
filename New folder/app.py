import streamlit as st
import pandas as pd
from rembg import remove
from PIL import Image
import io
import base64

# إعدادات الصفحة
st.set_page_config(page_title="مدير المنتجات الذكي", layout="wide")

# تهيئة مخزن البيانات (Session State) للحفاظ على البيانات أثناء التشغيل
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
        with st.spinner("جاري المعالجة... انتظر قليلاً"):
            # 1. حذف الخلفية
            input_image = Image.open(uploaded_file)
            output_image = remove(input_image)
            
            # 2. الضغط والتحويل لروابط (بشكل وهمي كـ Base64 لغرض العرض)
            buffered = io.BytesIO()
            output_image.save(buffered, format="PNG", optimize=True, quality=50)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # هنا نفترض أن الرابط هو رابط محلي أو رابط خدمة رفع
            fake_url = f"https://img-host.com/product_{len(st.session_state.product_list)}.png"
            
            # تحديث حالة الرابط في التطبيق
            st.session_state.temp_url = fake_url
            
            with col2:
                st.image(output_image, caption="الصورة المعالجة", width=250)
                st.success("تمت المعالجة! الرابط جاهز في الحقل أدناه.")

st.markdown("---")

# القسم الثاني: إدخال البيانات
st.header("2. تفاصيل المنتج")

col_a, col_b, col_c = st.columns(3)

with col_a:
    name = st.text_input("اسم المنتج")
    
with col_b:
    price = st.number_input("السعر", min_value=0, step=250, format="%d")

with col_c:
    # حقل الفئة الذكي
    category_option = st.selectbox("اختر الفئة", options=st.session_state.categories + ["+ إضافة فئة جديدة"])
    
    if category_option == "+ إضافة فئة جديدة":
        new_cat = st.text_input("اكتب اسم الفئة الجديدة")
        if st.button("حفظ الفئة"):
            if new_cat and new_cat not in st.session_state.categories:
                st.session_state.categories.append(new_cat)
                st.rerun()
    else:
        category = category_option

# حقل رابط الصورة (يتم ملؤه تلقائياً)
image_url = st.text_input("رابط الصورة (سيظهر هنا تلقائياً بعد المعالجة)", value=st.session_state.temp_url)

if st.button("إضافة المنتج للقائمة"):
    if name and image_url:
        new_product = {
            "الاسم": name,
            "السعر": price,
            "الفئة": category_option,
            "رابط الصورة": image_url
        }
        st.session_state.product_list.append(new_product)
        st.session_state.temp_url = "" # تصفير الحقل للعملية القادمة
        st.success("تمت إضافة المنتج بنجاح!")
    else:
        st.error("يرجى التأكد من كتابة الاسم ووجود رابط الصورة.")

st.markdown("---")

# القسم الثالث: العرض والتصدير
st.header("3. جدول المنتجات والتصدير")

if st.session_state.product_list:
    df = pd.DataFrame(st.session_state.product_list)
    st.table(df)
    
    # تحويل البيانات إلى Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Products')
    
    st.download_button(
        label="📥 تحميل الجدول كملف Excel",
        data=output.getvalue(),
        file_name="products_list.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("لا توجد منتجات مضافة حالياً.")
