import streamlit as st

st.title("⚙️ Настройки")

st.write(f"**Никнейм:** {st.session_state.nickname}")
st.write(f"**ID пользователя:** {st.session_state.user_id}")

st.divider()

st.subheader("О приложении")

st.info("""
**Mintellect** — приложение для управления школьными заметками и расписанием.

🐺 Версия: 1.0.0
""")

st.divider()

st.subheader("Подключение к API")

api_url = st.text_input("API URL", value="http://localhost:8000/api")

if st.button("Проверить подключение"):
    try:
        import requests
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            st.success("✅ Подключение к API успешно!")
            st.json(response.json())
        else:
            st.error(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Не удалось подключиться: {e}")

st.divider()

if st.button("Выйти из аккаунта", type="primary"):
    logout()
