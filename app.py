import streamlit as st
import pandas as pd

# ===============================
# إعدادات الصفحة
# ===============================
st.set_page_config(
    page_title="مدير المنتجات - تخصيص كامل",
    layout="wide"
)

# ===============================
# تهيئة الحالة
# ===============================
if "product_list" not in st.session_state:
    st.session_state.product_list = []

if "columns" not in st.session_state:
    st.session_state.columns = ["الاسم", "السعر", "الفئة", "الصورة"]

st.title("⚙️ نظام إدارة المنتجات (تحكم كامل بالحقول)")

# ===============================
# إعدادات الحقول
# ===============================
with st.expander("🛠️ إعدادات الحقول والأعمدة"):
    col1, col2 = st.columns(2)

    # ➕ إضافة حقل
    with col1:
        with st.form("add_column_form", clear_on_submit=True):
            raw_col = st.text_input("➕ أضف حقل جديد")
            add_submitted = st.form_submit_button("إضافة الحقل")

            if add_submitted:
                new_col = raw_col.strip()
                existing_cols = [c.strip().lower() for c in st.session_state.columns]

                if not new_col:
                    st.warning("اكتب اسم الحقل أولاً")
                elif new_col.lower() in existing_cols:
                    st.warning("هذا الحقل موجود بالفعل")
                else:
                    st.session_state.columns.append(new_col)
                    st.success(f"تمت إضافة الحقل: {new_col}")

    # 🗑️ حذف حقل
    with col2:
        with st.form("delete_column_form"):
            del_col = st.selectbox("🗑️ حذف حقل", st.session_state.columns)
            del_submitted = st.form_submit_button("حذف الحقل")

            if del_submitted:
                if del_col in st.session_state.columns:
                    st.session_state.columns.remove(del_col)
                    for p in st.session_state.product_list:
                        p.pop(del_col, None)
                    st.warning(f"تم حذف الحقل: {del_col}")

# ===============================
# إضافة منتج
# ===============================
st.subheader("➕ إضافة منتج جديد")

new_product = {}

for col in st.session_state.columns:
    if col == "السعر":
        new_product[col] = st.number_input(col, min_value=0.0, step=0.5)

    elif col == "الصورة":
        img_url = st.text_input("رابط الصورة")
        new_product[col] = img_url

        if img_url:
            st.image(img_url, width=150)

    else:
        new_product[col] = st.text_input(col)

if st.button("✅ إضافة المنتج"):
    st.session_state.product_list.append(new_product)
    st.success("تمت إضافة المنتج بنجاح")

# ===============================
# عرض المنتجات
# ===============================
st.subheader("📦 المنتجات")

if st.session_state.product_list:
    df = pd.DataFrame(st.session_state.product_list)

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic"
    )

    st.session_state.product_list = edited_df.to_dict(orient="records")

    st.download_button(
        "📥 تحميل Excel",
        edited_df.to_csv(index=False),
        file_name="products.csv",
        mime="text/csv"
    )
else:
    st.info("لا توجد منتجات بعد")