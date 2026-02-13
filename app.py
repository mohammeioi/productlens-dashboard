import streamlit as st
import pandas as pd
from PIL import Image
import io

# محاولة استيراد مكتبة إزالة الخلفية
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except Exception:
    REMBG_AVAILABLE = False

# ===============================
# إعدادات الصفحة
# ===============================
st.set_page_config(
    page_title="مدير المنتجات الاحترافي",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# تهيئة الحالة (Session State)
# ===============================
if "product_list" not in st.session_state:
    st.session_state.product_list = []

if "columns" not in st.session_state:
    st.session_state.columns = ["الاسم", "السعر", "الفئة", "الصورة"]

# ===============================
# الشريط الجانبي (الإعدادات)
# ===============================
with st.sidebar:
    st.title("⚙️ الإعدادات")
    st.subheader("تحكم في أعمدة الجدول")
    
    # إضافة حقل جديد
    with st.expander("➕ إضافة حقل جديد"):
        new_col_input = st.text_input("اسم الحقل")
        if st.button("إضافة"):
            if new_col_input and new_col_input not in st.session_state.columns:
                st.session_state.columns.append(new_col_input)
                st.rerun()
    
    # حذف حقل
    with st.expander("🗑️ حذف حقل"):
        col_to_del = st.selectbox("اختر الحقل", st.session_state.columns)
        if st.button("تأكيد الحذف"):
            st.session_state.columns.remove(col_to_del)
            st.rerun()

# ===============================
# الواجهة الرئيسية
# ===============================
st.title("📦 نظام إدارة المنتجات الذكي")

# استخدام Tabs لتنظيم العرض ومنع تداخل الحقول
tab1, tab2 = st.tabs(["📋 عرض المنتجات", "➕ إضافة منتج جديد"])

with tab2:
    st.subheader("تعبئة بيانات المنتج")
    
    # استخدام form لمنع التحديث التلقائي أثناء الكتابة
    with st.form("product_entry_form", clear_on_submit=True):
        new_product = {}
        
        # تقسيم الحقول إلى أعمدة لجعل التصميم أجمل
        cols_grid = st.columns(2)
        
        for i, col in enumerate(st.session_state.columns):
            # توزيع الحقول على العمودين بالتناوب
            current_col = cols_grid[i % 2]
            
            if col == "السعر":
                new_product[col] = current_col.number_input(col, min_value=0, step=1)
            
            elif col == "الصورة":
                uploaded = current_col.file_uploader("اختر صورة", type=["png", "jpg", "jpeg"])
                new_product[col] = uploaded # سنعالج الصورة عند الضغط على زر الحفظ
            
            elif col == "الفئة":
                new_product[col] = current_col.selectbox(col, ["عام", "إلكترونيات", "أثاث", "ملابس"])
                
            else:
                new_product[col] = current_col.text_input(col)
        
        # خيار إزالة الخلفية
        remove_bg_toggle = st.checkbox("🪄 تفعيل إزالة الخلفية تلقائياً (عند رفع صورة)")
        
        submit_btn = st.form_submit_button("💾 حفظ المنتج في القائمة")

        if submit_btn:
            # معالجة الصورة قبل الحفظ
            if new_product.get("الصورة"):
                img = Image.open(new_product["الصورة"])
                if remove_bg_toggle and REMBG_AVAILABLE:
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="PNG")
                    processed_img = remove(img_bytes.getvalue())
                    img = Image.open(io.BytesIO(processed_img))
                
                # تحويل الصورة إلى Bytes لتخزينها
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                new_product["الصورة"] = buf.getvalue()
            
            st.session_state.product_list.append(new_product)
            st.success("✅ تم حفظ المنتج!")

with tab1:
    if st.session_state.product_list:
        df = pd.DataFrame(st.session_state.product_list)
        
        # عرض الإحصائيات سريعة
        st.info(f"إجمالي المنتجات: {len(df)}")
        
        # محرر البيانات التفاعلي
        st.subheader("تعديل البيانات مباشرة من الجدول")
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "الصورة": st.column_config.ImageColumn("معاينة الصورة")
            }
        )
        
        # تحديث القائمة بناءً على التعديلات في الجدول
        if st.button("💾 حفظ تعديلات الجدول"):
            st.session_state.product_list = edited_df.to_dict(orient="records")
            st.rerun()

        # تصدير Excel
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            edited_df.to_excel(writer, index=False)
        
        st.download_button(
            "📥 تحميل ملف Excel المعدل",
            excel_buffer.getvalue(),
            file_name="products_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ القائمة فارغة حالياً. انتقل لتبويب الإضافة.")
