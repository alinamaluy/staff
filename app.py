import streamlit as st
import pandas as pd
from math import ceil
from datetime import datetime

# Нормы по умолчанию для каждой должности
ROLE_DEFAULTS = {
    "Официант": {"order_norm": 30, "label": "Норма заказов на официанта"},
    "Бармен": {"order_norm": 60, "label": "Норма напитков на бармена"},
    "Хостес": {"order_norm": 80, "label": "Количество гостей на 1 хостес"},
    "Шеф-повар": {"order_norm": 50, "label": "Количество блюд на одного повара"},
    "Посудомойщик": {"order_norm": 100, "label": "Количество гостей, посуду которых обслуживает 1 человек"},
    "Уборщица": {"order_norm": 150, "label": "Количество гостей на 1 уборщицу"}
}

def calculate_staff_from_orders(
    orders_per_day,
    order_norm_per_staff,
    shifts_per_day,
    restaurant_days_per_week,
    staff_days_per_week,
    shifts_per_staff_per_day,
    position="Сотрудник"
):
    total_orders_per_week = orders_per_day * restaurant_days_per_week
    orders_per_shift = orders_per_day / shifts_per_day
    staff_per_shift = ceil(orders_per_shift / order_norm_per_staff)
    total_weekly_shifts = staff_per_shift * shifts_per_day * restaurant_days_per_week
    effective_shifts_per_staff = staff_days_per_week * shifts_per_staff_per_day
    required_staff = ceil(total_weekly_shifts / effective_shifts_per_staff)

    data = {
        "Должность": position,
        "Объектов обслуживания в день": f"{orders_per_day}",
        "Смен в день": f"{shifts_per_day}",
        "Норма на 1 сотрудника": f"{order_norm_per_staff}",
        "Объектов в смену": f"{orders_per_shift:.1f}",
        "Сотрудников на смену": f"{staff_per_shift}",
        "Смен в неделю (всего)": f"{total_weekly_shifts}",
        "Смен в неделю (1 сотрудник)": f"{effective_shifts_per_staff}",
        "Необходимое количество сотрудников": f"{required_staff}"
    }

    return pd.DataFrame.from_dict(data, orient='index', columns=["Значение"])


st.set_page_config(page_title="Расчет штата ресторана", layout="centered")
st.title("👥 Калькулятор штата сотрудников ресторана")
st.markdown("Выберите роль и введите параметры для расчета нужного количества сотрудников:")

with st.form("input_form"):
    position = st.selectbox("Выберите должность", list(ROLE_DEFAULTS.keys()))
    orders_per_day = st.slider("Количество заказов / гостей / объектов обслуживания в день", 20, 500, 120, step=10)

    norm_label = ROLE_DEFAULTS[position]["label"]
    default_norm = ROLE_DEFAULTS[position]["order_norm"]
    order_norm = st.slider(norm_label, 10, 200, default_norm, step=5)

    shifts_per_day = st.slider("Смен в день", 1, 3, 2)
    restaurant_days = st.slider("Дней работы ресторана в неделю", 1, 7, 7)
    staff_days = st.slider("Дней работы сотрудника в неделю", 1, 7, 5)
    shifts_per_staff = st.slider("Смен в день на 1 сотрудника", 1, 2, 1)

    submitted = st.form_submit_button("🔍 Рассчитать")

if submitted:
    df = calculate_staff_from_orders(
        orders_per_day,
        order_norm,
        shifts_per_day,
        restaurant_days,
        staff_days,
        shifts_per_staff,
        position
    )

    st.success("✅ Расчет завершен!")
    st.dataframe(df)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"staff_calculation_{now}.xlsx"
    df.to_excel(filename, engine="openpyxl")

    with open(filename, "rb") as f:
        st.download_button("📥 Скачать результат в Excel", f, file_name=filename)
