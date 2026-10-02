import datetime
import pandas as pd
import streamlit as st

# إعداد الصفحة والتصميم الجمالي
st.set_page_config(
    page_title="إدارة المخزون والمبيعات",
    page_icon="🛍️",
    layout="wide",
)

# تخصيص الألوان والتصميم عبر CSS لتحسين شكل التطبيق
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    h1, h2, h3 {
        color: #1e293b;
    }
    .stButton>button {
        background-color: #0284c7;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0369a1;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# عنوان التطبيق الرئيسي
st.markdown(
    "<h1 style='text-align: center; color: #0284c7;'>🛍️ نظام إدارة المحل والمخزون</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #64748b;'>تطبيقك الذكي لمتابعة المنتجات، المبيعات، والأرباح بكل سهولة</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# تهيئة بيانات المخزون والمبيعات في ذاكرة الجلسة
if "inventory" not in st.session_state:
  st.session_state.inventory = pd.DataFrame({
      "رقم المنتج": [1, 2],
      "اسم السلعة": ["عامل أول", "عامل إضافي"],
      "السعر (د.ج)": [150.0, 130.0],
      "الكمية": [0, 5],
      "الحد الأدنى": [5, 5],
  })

if "sales" not in st.session_state:
  st.session_state.sales = pd.DataFrame(
      columns=["التاريخ", "اسم السلعة", "الكمية المباعة", "الإجمالي (د.ج)"]
  )

# حساب الإحصائيات العامة
total_products = len(st.session_state.inventory)
low_stock_df = st.session_state.inventory[
    st.session_state.inventory["الكمية"]
    <= st.session_state.inventory["الحد الأدنى"]
]
low_stock_count = len(low_stock_df)

today_str = datetime.date.today().strftime("%Y-%m-%d")
today_sales = st.session_state.sales[
    st.session_state.sales["التاريخ"] == today_str
]
total_revenue_today = (
    today_sales["الإجمالي (د.ج)"].sum() if not today_sales.empty else 0.0
)
pending_orders = 0  # الطلبات المعلقة افتراضياً

# عرض لوحة المؤشرات (Dashboard Metrics)
col1, col2, col3, col4 = st.columns(4)
with col1:
  st.metric(
      label="💰 مبيعات اليوم (د.ج)", value=f"{total_revenue_today:,.2f}"
  )
with col2:
  st.metric(label="📦 إجمالي المنتجات", value=total_products)
with col3:
  st.metric(label="⏳ الطلبات المعلقة", value=pending_orders)
with col4:
  st.metric(label="⚠️ مخزون منخفض", value=low_stock_count)

st.markdown("---")

# الشريط الجانبي للتنقل بين الأقسام
st.sidebar.title("📌 القائمة الرئيسية")
app_mode = st.sidebar.selectbox(
    "اختر القسم:", ["🏠 الرئيسية", "📦 إدارة المخزون", "🛒 نقطة البيع (تسجيل بيع)"]
)

if app_mode == "🏠 الرئيسية":
  st.subheader("📊 نظرة عامة على حالة المحل")
  if not low_stock_df.empty:
    st.warning("⚠️ تنبيه: توجد منتجات وشحكات وصل حدها الأدنى في المخزون!")
    st.dataframe(low_stock_df, use_container_width=True)
  else:
    st.success("✅ جميع المنتجات متوفرة وبكميات جيدة في المخزون.")

  st.markdown("### 📈 سجل مبيعات اليوم")
  if not today_sales.empty:
    st.dataframe(today_sales, use_container_width=True)
  else:
    st.info("لا توجد مبيعات مسجلة لهذا اليوم حتى الآن.")

elif app_mode == "📦 إدارة المخزون":
  st.subheader("📦 إدارة وتعديل المنتجات")
  st.dataframe(st.session_state.inventory, use_container_width=True)

  st.markdown("### ➕ إضافة منتج جديد")
  with st.form("add_product_form"):
    new_name = st.text_input("اسم السلعة / المنتج")
    new_price = st.number_input("السعر (د.ج)", min_value=0.0, value=100.0)
    new_qty = st.number_input("الكمية المتوفرة", min_value=0, value=10)
    new_min = st.number_input("الحد الأدنى للتنبيه", min_value=0, value=3)
    submit_btn = st.form_submit_button("إضافة للمخزون")

    if submit_btn and new_name:
      new_id = (
          int(st.session_state.inventory["رقم المنتج"].max()) + 1
          if not st.session_state.inventory.empty
          else 1
      )
      new_row = pd.DataFrame({
          "رقم المنتج": [new_id],
          "اسم السلعة": [new_name],
          "السعر (د.ج)": [new_price],
          "الكمية": [new_qty],
          "الحد الأدنى": [new_min],
      })
      st.session_state.inventory = pd.concat(
          [st.session_state.inventory, new_row], ignore_index=True
      )
      st.success(f"تمت إضافة المنتج '{new_name}' بنجاح!")
      st.rerun()

elif app_mode == "🛒 نقطة البيع (تسجيل بيع)":
  st.subheader("🛒 تسجيل عملية بيع جديدة")
  if st.session_state.inventory.empty:
    st.warning("الرجاء إضافة منتجات أولاً من قسم إدارة المخزون.")
  else:
    product_names = st.session_state.inventory["اسم السلعة"].tolist()
    selected_product = st.selectbox("اختر السلعة المراد بيعها", product_names)
    qty_to_sell = st.number_input("الكمية المباعة", min_value=1, value=1)

    if st.button("تأكيد البيع"):
      product_row = st.session_state.inventory[
          st.session_state.inventory["اسم السلعة"] == selected_product
      ].index[0]
      current_qty = st.session_state.inventory.loc[product_row, " الكمية" if " الكمية" in st.session_state.inventory.columns else "الكمية"] # type: ignore
      
      # تصحيح مباشر لاسم عمود الكمية
      qty_col = "الكمية" if "الكمية" in st.session_state.inventory.columns else " الكمية"
      current_qty = st.session_state.inventory.loc[product_row, qty_col]

      if current_qty >= qty_to_sell:
        price = st.session_state.inventory.loc[product_row, "السعر (د.ج)"]
        total_price = price * qty_to_sell

        # خصم الكمية من المخزون
        st.session_state.inventory.loc[product_row, qty_col] = (
            current_qty - qty_to_sell
        )

        # تسجيل المبيعات
        new_sale = pd.DataFrame({
            "التاريخ": [today_str],
            "اسم السلعة": [selected_product],
            "الكمية المباعة": [qty_to_sell],
            "الإجمالي (د.ج)": [total_price],
        })
        st.session_state.sales = pd.concat(
            [st.session_state.sales, new_sale], ignore_index=True
        )

        st.success(
            f"✅ تم بيع {qty_to_sell} من '{selected_product}' بمبلغ"
            f" {total_price} د.ج بنجاح!"
        )
        st.rerun()
      else:
        st.error("❌ الكمية المتوفرة في المخزون غير كافية لإتمام البيع!")
