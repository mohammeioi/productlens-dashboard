import streamlit as st
import pandas as pd
import cloudinary
import cloudinary.uploader
from io import BytesIO

# ===============================
# 1. إعدادات Cloudinary الخاصة بك
# ===============================
cloudinary.config( 
  cloud_name = "dnkjwxkrp", 
  api_key = "183137181334566", 
  api_secret = "Amyk9rxJeAmDcsyzienGVuXshQc",
  secure = True
)

st.set_page_config(page_title="مدير المنتجات الذكي", layout="wide", page_icon="🛍️")

if "product_list" not in st.session_state:
    st.session_state.product_list = []

st.title("🛍️ نظام إدارة المنتجات (حل مشكلة تبديل الكاميرا)")

# ===============================
# 2. إضافة منتج جديد
# ===============================
col1, col2 = st.columns([1, 1])

with col1:
    # ملاحظة: أخرجنا اختيار المصدر خارج الـ Form لضمان استجابة واجهة المستخدم فوراً
    st.subheader("➕ تفاصيل المنتج")
    
    name = st.text_input("اسم المنتج", key="prod_name")
    price = st.number_input("السعر", min_value=0.0, step=0.1, key="prod_price")
    
    categories = ["إلكترونيات", "ملابس", "أدوات منزلية", "أغذية", "عطور", "أخرى"]
    category_selection = st.selectbox("اختر الفئة", categories)
    
    final_category = category_selection
    if category_selection == "أخرى":
        final_category = st.text_input("اكتب الفئة الجديدة هنا")

    st.write("---")
    # اختيار مصدر الصورة
    source = st.radio("مصدر الصورة:", ("الكاميرا 📷", "رفع ملف 📁"), key="img_source")
    
    # الحل: استخدام حاوية شرطية لضمان إغلاق الكاميرا تماماً عند اختيار ملف
    uploaded_file = None
    if source == "الكاميرا 📷":
        # إضافة مفتاح فريد (key) يضمن إعادة تشغيل المكون عند التبديل
        uploaded_file = st.camera_input("التقط صورة", key="camera_widget")
    else:
        uploaded_file = st.file_uploader("اختر صورة من الجهاز", type=["jpg", "png", "jpeg"], key="file_widget")

    # زر الحفظ خارج الفورم أو داخله، سنبقيه بسيطاً هنا
    if st.button("حفظ ورفع المنتج ✅"):
        if uploaded_file and name and final_category:
            with st.spinner('جاري الرفع لـ Cloudinary...'):
                try:
                    upload_result = cloudinary.uploader.upload(uploaded_file)
                    img_url = upload_result["secure_url"]
                    
                    st.session_state.product_list.append({
                        "الاسم": name,
                        "السعر": price,
                        "الفئة": final_category,
                        "رابط_الصورة": img_url
                    })
                    st.success(f"تمت إضافة {name} بنجاح!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ في الرفع: {e}")
        else:
            st.warning("⚠️ تأكد من ملء الاسم، الفئة، والتقاط/رفع الصورة")

# ===============================
# 3. عرض البيانات وتصدير Excel
# ===============================
with col2:
    st.subheader("📦 جدول المنتجات")
    if st.session_state.product_list:
        df = pd.DataFrame(st.session_state.product_list)
        st.data_editor(df, column_config={"رابط_الصورة": st.column_config.LinkColumn("الرابط المباشر")}, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button("📥 تحميل Excel", data=output.getvalue(), file_name="products.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        if st.button("🗑️ مسح القائمة"):
            st.session_state.product_list = []
            st.rerun()