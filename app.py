from datetime import datetime
import pandas as pd
import streamlit as st

# إعدادات الصفحة وتصميم الواجهة
st.set_page_config(
    page_title="نظام إدارة المحلات - Mahaal Clone", page_icon="🛍️", layout="wide"
)

# تخصيص التصميم ودعم اللغة العربية (RTL)
st.markdown(
    """
    <style>
    body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        background-color: #f8f9fa;
        font-family: 'Cairo', sans-serif;
    }
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #1e3932;
        margin-bottom: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# تهيئة قاعدة البيانات الوهمية في الذاكرة (Session State)
if "inventory" not in st.session_state:
  st.session_state.inventory = pd.DataFrame(
      {
          "معرف المنتج": ["P001", "P002", "P003"],
          "اسم المنتج": ["زيت زيتون 1ل", "سكر 1كغ", "حليب نصف دسم"],
          "سعر الشراء": [650.0, 120.0, 95.0],
          "سعر البيع": [750.0, 140.0, 110.0],
          "الكمية": [45, 120, 30],
          "الحد الأدنى": [10, 20, 15],
      }
  )

if "sales" not in st.session_state:
  st.session_state.sales = pd.DataFrame(
      columns=[
          "رقم الفاتورة",
          "التاريخ",
          "المنتج",
          "الكمية المباعة",
          "سعر البيع",
          "الإجمالي",
      ]
  )

if "debts" not in st.session_state:
  st.session_state.debts = pd.DataFrame(
      columns=["اسم العميل", "المبلغ الإجمالي", "المدفوع", "المتبقي", "الحالة"]
  )

# القائمة الجانبية للتنقل (Sidebar)
st.sidebar.title("🛍️ متجري (Mahaal)")
st.sidebar.markdown("---")
menu = st.sidebar.selectbox(
    "القائمة الرئيسية",
    [
        "📊 لوحة التحكم",
        "🛒 نقطة البيع (POS)",
        "📦 إدارة المخزون",
        "👥 ديون العملاء",
        "📈 التقارير",
    ],
)

# 1. لوحة التحكم (Dashboard)
if menu == "📊 لوحة التحكم":
  st.markdown(
      '<p class="main-header">📊 لوحة التحكم والأداء</p>', unsafe_allow_html=True
  )

  total_products = len(st.session_state.inventory)
  total_stock_value = (
      st.session_state.inventory["سعر الشراء"]
      * st.session_state.inventory["الكمية"]
  ).sum()

  today_str = datetime.now().strftime("%Y-%m-%d")
  today_sales = st.session_state.sales[
      st.session_state.sales["التاريخ"].str.startswith(today_str)
  ]
  today_revenue = (
      today_sales["الإجمالي"].sum() if not today_sales.empty else 0.0
  )

  col1, col2, col3 = st.columns(3)
  with col1:
    st.metric(label="إجمالي مبيعات اليوم", value=f"{today_revenue:,.2f} د.ج")
  with col2:
    st.metric(label="قيمة المخزون الحالي", value=f"{total_stock_value:,.2f} د.ج")
  with col3:
    st.metric(label="عدد أصناف المنتجات", value=total_products)

  st.markdown("---")
  st.subheader("⚠️ تنبيهات انخفاض المخزون")
  low_stock = st.session_state.inventory[
      st.session_state.inventory["الكمية"]
      <= st.session_state.inventory["الحد الأدنى"]
  ]
  if not low_stock.empty:
    st.dataframe(low_stock, use_container_width=True)
  else:
    st.success("جميع المنتجات متوفرة بكميات كافية.")

# 2. نقطة البيع (POS)
elif menu == "🛒 نقطة البيع (POS)":
  st.markdown(
      '<p class="main-header">🛒 تسجيل مبيعات جديدة</p>', unsafe_allow_html=True
  )

  if st.session_state.inventory.empty:
    st.warning("الرجاء إضافة منتجات إلى المخزون أولاً.")
  else:
    product_list = st.session_state.inventory["اسم المنتج"].tolist()
    selected_product = st.selectbox("اختر المنتج للبيع", product_list)

    product_row = st.session_state.inventory[
        st.session_state.inventory["اسم المنتج"] == selected_product
    ].iloc[0]
    available_qty = product_row["الكمية"]
    unit_price = product_row["سعر البيع"]

    st.info(
        f"السعر: {unit_price} د.ج | الكمية المتوفرة في المخزون: {available_qty}"
    )

    quantity_sold = st.number_input(
        "الكمية المباعة", min_value=1, max_value=int(available_qty), value=1
    )
    total_price = quantity_sold * unit_price

    st.markdown(f"### الإجمالي المطلوب: **{total_price:,.2f} د.ج**")

    if st.button("✅ إتمام البيع وخفض المخزون", type="primary"):
      st.session_state.inventory.loc[
          st.session_state.inventory["اسم المنتج"] == selected_product, "الكمية"
      ] -= quantity_sold

      new_sale = pd.DataFrame(
          {
              "رقم الفاتورة": [f"INV-{len(st.session_state.sales)+1:04d}"],
              "التاريخ": [datetime.now().strftime("%Y-%m-%d %H:%M")],
              "المنتج": [selected_product],
              "الكمية المباعة": [quantity_sold],
              "سعر البيع": [unit_price],
              "الإجمالي": [total_price],
          }
      )
      st.session_state.sales = pd.concat(
          [st.session_state.sales, new_sale], ignore_index=True
      )
      st.success("تم إتمام عملية البيع بنجاح وتحديث المخزون!")

    st.markdown("---")
    st.subheader("📋 سجل مبيعات اليوم")
    if not st.session_state.sales.empty:
      st.dataframe(st.session_state.sales, use_container_width=True)

# 3. إدارة المخزون
elif menu == "📦 إدارة المخزون":
  st.markdown(
      '<p class="main-header">📦 إدارة المخزون والمنتجات</p>',
      unsafe_allow_html=True,
  )

  tab1, tab2 = st.tabs(["عرض المخزون", "إضافة منتج جديد"])

  with tab1:
    st.dataframe(st.session_state.inventory, use_container_width=True)

  with tab2:
    with st.form("add_product_form"):
      col1, col2 = st.columns(2)
      with col1:
        p_id = st.text_input(
            "معرف المنتج", f"P00{len(st.session_state.inventory)+1}"
        )
        p_name = st.text_input("اسم المنتج")
        p_buy = st.number_input("سعر الشراء (د.ج)", min_value=0.0, value=100.0)
      with col2:
        p_sell = st.number_input("سعر البيع (د.ج)", min_value=0.0, value=120.0)
        p_qty = st.number_input("الكمية الأولية", min_value=0, value=10)
        p_min = st.number_input("حد التنبيه الأدنى", min_value=0, value=5)

      submitted = st.form_submit_button("حفظ وإضافة المنتج")
      if submitted and p_name:
        new_item = pd.DataFrame(
            {
                "معرف المنتج": [p_id],
                "اسم المنتج": [p_name],
                "سعر الشراء": [p_buy],
                "سعر البيع": [p_sell],
                "الكمية": [p_qty],
                "الحد الأدنى": [p_min],
            }
        )
        st.session_state.inventory = pd.concat(
            [st.session_state.inventory, new_item], ignore_index=True
        )
        st.success(f"تمت إضافة المنتج '{p_name}' بنجاح!")

# 4. ديون العملاء
elif menu == "👥 ديون العملاء":
  st.markdown(
      '<p class="main-header">👥 دفتر ديون وحسابات العملاء</p>',
      unsafe_allow_html=True,
  )

  with st.form("debt_form"):
    c_name = st.text_input("اسم العميل")
    c_total = st.number_input("إجمالي الدين (د.ج)", min_value=0.0, value=0.0)
    c_paid = st.number_input("المبلغ المدفوع (د.ج)", min_value=0.0, value=0.0)
    submitted_debt = st.form_submit_button("حفظ سجل الدين")

    if submitted_debt:
      c_remaining = c_total - c_paid
      c_status = "خالص" if c_remaining <= 0 else "مستحق"
      new_debt = pd.DataFrame(
          {
              "اسم العميل": [c_name],
              "المبلغ الإجمالي": [c_total],
              "المدفوع": [c_paid],
              "المتبقي": [c_remaining],
              "الحالة": [c_status],
          }
      )
      st.session_state.debts = pd.concat(
          [st.session_state.debts, new_debt], ignore_index=True
      )
      st.success("تم تسجيل حساب العميل بنجاح!")

  if not st.session_state.debts.empty:
    st.dataframe(st.session_state.debts, use_container_width=True)

# 5. التقارير
elif menu == "📈 التقارير":
  st.markdown(
      '<p class="main-header">📈 التقارير المالية وحركة المبيعات</p>',
      unsafe_allow_html=True,
  )
  if not st.session_state.sales.empty:
    total_sales_sum = st.session_state.sales["الإجمالي"].sum()
    st.metric(label="إجمالي المبيعات التراكمية", value=f"{total_sales_sum:,.2f} د.ج")
    st.dataframe(st.session_state.sales, use_container_width=True)
  else:
    st.info("لا توجد بيانات كافية لعرض التقارير حالياً.")
