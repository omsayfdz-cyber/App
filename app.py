import datetime
import pandas as pd
import streamlit as st

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title="إدارة المخزون والمبيعات", page_icon="📦", layout="centered"
)

# تهيئة قاعدة البيانات المحلية المؤقتة في الذاكرة
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(
        {
            "رقم المنتج": [1, 2],
            "اسم السلعة": ["سامبل ازرق", "سامبل اصفر"],
            "السعر (د.ج)": [150.0, 150.0],
            "الكمية": [0, 0],
            "الحد الأدنى": [5, 5],
        }
    )

if "sales" not in st.session_state:
    st.session_state.sales = pd.DataFrame(
        columns=["التاريخ", "اسم السلعة", "الكمية المباعة", "الإجمالي (د.ج)"]
    )

# العنوان الرئيسي ولوحة التحكم
st.markdown(
    "<h2 style='text-align: right; direction: rtl;'>لوحة التحكم 📊</h2>",
    unsafe_allow_html=True,
)

# حساب الإحصائيات
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

# عرض الإحصائيات (مؤشرات رئيسية شبيهة بالصورة)
col1, col2 = st.columns(2)
with col1:
    st.metric(label="مبيعات اليوم (د.ج)", value=f"{total_revenue_today:,.2f}")
    st.metric(label="إجمالي المنتجات", value=total_products)
with col2:
    st.metric(label="الطلبات المعلقة", value="0")
    st.metric(label="عناصر المخزون المنخفض", value=low_stock_count)

st.markdown("---")

# القائمة الجانبية أو الأزرار السريعة للعمليات
menu = st.sidebar.selectbox(
    "القائمة الرئيسية",
    [
        "🏠 الرئيسية",
        "➕ إضافة منتج جديد",
        "🛒 إنشاء طلب / بيع",
        "📦 المخزن وإعادة التعبئة",
        "📊 سجل المبيعات",
    ],
)

if menu == "🏠 الرئيسية":
    st.markdown(
        "<h3 style='text-align: right; direction: rtl;'>تنبيه مخزون منخفض ⚠️</h3>",
        unsafe_allow_html=True,
    )

    if not low_stock_df.empty:
        for index, row in low_stock_df.iterrows():
            st.warning(
                f"⚠️ **{row['اسم السلعة']}** - المخزون المتبقي: **{row[' الكمية']} قطعة** | السعر: {row['السعر (د.ج)']} د.ج"
            )
    else:
        st.success("جميع المنتجات متوفرة ولا يوجد مخزون منخفض حالياً! ✅")

elif menu == "➕ إضافة منتج جديد":
    st.markdown(
        "<h3 style='text-align: right; direction: rtl;'>إضافة منتج جديد للمخزن</h3>",
        unsafe_allow_html=True,
    )

    with st.form("add_product_form"):
        prod_name = st.text_input("اسم السلعة")
        prod_price = st.number_input("السعر (د.ج)", min_value=0.0, value=100.0)
        prod_qty = st.number_input("الكمية الأولية", min_value=0, value=10)
        min_limit = st.number_input("حد تنبيه انخفاض المخزون", min_value=0, value=3)

        submit_btn = st.form_submit_button("حفظ المنتج")

        if submit_btn:
            if prod_name:
                new_id = (
                    st.session_state.inventory["رقم المنتج"].max() + 1
                    if not st.session_state.inventory.empty
                    else 1
                )
                new_row = pd.DataFrame(
                    {
                        "رقم المنتج": [new_id],
                        "اسم السلعة": [prod_name],
                        "السعر (د.ج)": [prod_price],
                        "الكمية": [prod_qty],
                        "الحد الأدنى": [min_limit],
                    }
                )
                st.session_state.inventory = pd.concat(
                    [st.session_state.inventory, new_row], ignore_index=True
                )
                st.success(f"تمت إضافة المنتج '{prod_name}' بنجاح!")
            else:
                st.error("يرجى إدخال اسم السلعة على الأقل.")

elif menu == "🛒 إنشاء طلب / بيع":
    st.markdown(
        "<h3 style='text-align: right; direction: rtl;'>تسجيل عملية بيع جديدة</h3>",
        unsafe_allow_html=True,
    )

    if st.session_state.inventory.empty:
        st.warning("لا توجد منتجات في المخزن حالياً أضف بعض المنتجات أولاً.")
    else:
        product_list = st.session_state.inventory["اسم السلعة"].tolist()
        selected_product = st.selectbox("اختر السلعة للبيع", product_list)

        # جلب الكمية الحالية والسعر
        product_row = st.session_state.inventory[
            st.session_state.inventory["اسم السلعة"] == selected_product
        ].iloc[0]
        current_qty = product_row["الكمية"]
        unit_price = product_row["السعر (د.ج)"]

        st.info(
            f"الكمية المتاحة في المخزن: **{current_qty}** | السعر للقطعة: **{unit_price} د.ج**"
        )

        sell_qty = st.number_input(
            "الكمية المراد بيعها", min_value=1, max_value=max(1, current_qty), value=1
        )

        if st.button("إتمام البيع وتخفيض المخزون"):
            if current_qty >= sell_qty:
                # خصم الكمية من المخزن
                st.session_state.inventory.loc[
                    st.session_state.inventory["اسم السلعة"] == selected_product,
                    "الكمية",
                ] -= sell_qty

                # تسجيل المبيعات
                total_price = sell_qty * unit_price
                new_sale = pd.DataFrame(
                    {
                        "التاريخ": [today_str],
                        "اسم السلعة": [selected_product],
                        "الكمية المباعة": [sell_qty],
                        "الإجمالي (د.ج)": [total_price],
                    }
                )
                st.session_state.sales = pd.concat(
                    [st.session_state.sales, new_sale], ignore_index=True
                )

                st.success(
                    f"تمت عملية البيع بنجاح! الإجمالي: {total_price} د.ج. المتبقي في المخزن: {current_qty - sell_qty}"
                )
            else:
                st.error("الكمية المطلوبة أكبر من المخزون المتوفر!")

elif menu == "📦 المخزن وإعادة التعبئة":
    st.markdown(
        "<h3 style='text-align: right; direction: rtl;'>إدارة المخزن وإعادة التعبئة السريعة</h3>",
        unsafe_allow_html=True,
    )

    if st.session_state.inventory.empty:
        st.info("المخزن فارغ.")
    else:
        st.dataframe(st.session_state.inventory, use_container_width=True)

        st.markdown("#### ⚡ إعادة تعبئة سريعة للسلع")
        refill_product = st.selectbox(
            "اختر السلعة لإعادة تعبئتها",
            st.session_state.inventory["اسم السلعة"].tolist(),
            key="refill_select",
        )
        add_qty = st.number_input(
            "الكمية المضافة للمخزن", min_value=1, value=10, key="refill_qty"
        )

        if st.button("تحديث وزيادة المخزون فوراً"):
            st.session_state.inventory.loc[
                st.session_state.inventory["اسم السلعة"] == refill_product,
                "الكمية",
            ] += add_qty
            st.success(
                f"تمت إضافة {add_qty} قطعة إلى '{refill_product}' بنجاح! أصبحت الكمية الجديدة محدثة."
            )

elif menu == "📊 سجل المبيعات":
    st.markdown(
        "<h3 style='text-align: right; direction: rtl;'>سجل المبيعات اليومية</h3>",
        unsafe_allow_html=True,
    )
    if st.session_state.sales.empty:
        st.info("لا توجد مبيعات مسجلة حتى الآن.")
    else:
        st.dataframe(st.session_state.sales, use_container_width=True)
      
