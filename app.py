import json
import os
import subprocess

import streamlit as st

st.set_page_config(layout="wide")
st.title("Y Combinator Summer 2025 Parser + LinkedIn")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(
    BASE_DIR, "ycom_project", "output", "yc_companies.json"
)

if "run_flag" not in st.session_state:
    st.session_state.run_flag = False

if st.button("🔄 Запустить парсеры (YCombinator + LinkedIn)"):
    st.session_state.run_flag = True
    with st.spinner("⏳ Сбор данных с Y Combinator..."):
        subprocess.run(
            ["scrapy", "crawl", "y_com_spider"],
            cwd=os.path.join(BASE_DIR, "ycom_project")
        )
    with st.spinner("⏳ Обогащение через LinkedIn..."):
        subprocess.run(
            ["scrapy", "crawl", "linkedin_spider"],
            cwd=os.path.join(BASE_DIR, "ycom_project")
        )
    st.success("✅ Парсеры завершили работу! Данные обновлены.")

if os.path.exists(DATA_PATH):
    with open(DATA_PATH, encoding='utf-8') as f:
        data = json.load(f)

    st.subheader("📋 Все данные по компаниям")
    for i, company in enumerate(data):
        with st.expander(f"{i + 1}. {company.get('name', 'Без названия')}"):
            st.json(company)
else:
    if st.session_state.run_flag:
        st.warning(
            "Файл с данными не найден. "
            "Нажмите кнопку выше, чтобы запустить парсеры."
        )
