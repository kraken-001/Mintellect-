"""
Страница настроек.
"""
import streamlit as st
import requests
from api_client import BASE_URL
from ui_helpers import inject_css, page_header, sidebar_user_info

inject_css()
sidebar_user_info()
page_header("Настройки", "Настройки приложения")

# Информация о пользователе
st.subheader("👤 Профиль")
user = st.session_state.get("user", {})
st.write(f"**Никнейм:** {user.get('nickname', '-')}")
st.write(f"**ID:** {user.get('id', '-')}")

st.divider()

# Подключение к API
st.subheader("🔌 Подключение к API")

api_url = st.text_input("API URL", value=BASE_URL)

if st.button("Проверить подключение"):
    try:
        health_url = api_url.replace("/api", "") + "/api/health"
        response = requests.get(health_url, timeout=5)
        if response.ok:
            st.success("✅ Подключение успешно!")
            st.json(response.json())
        else:
            st.error(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Не удалось подключиться: {e}")

st.divider()

# О приложении
st.subheader("ℹ️ О приложении")
st.info("""
**Mintellect** 🐺

Умный дневник для школьника.

Версия: 1.0.0
""")