"""
Mintellect — точка входа.
Запуск: streamlit run app.py
"""
import streamlit as st
from ui_helpers import inject_css, sidebar_user_info

st.set_page_config(
    page_title="Mintellect",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
sidebar_user_info()

if not st.session_state.get("token"):
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;min-height:60vh;text-align:center;">
        <div style="font-family:'DM Serif Display',serif;font-size:3rem;
                    color:#e8c76a;margin-bottom:12px;">🐺 Mintellect</div>
        <div style="color:#8890a6;font-size:14px;margin-bottom:32px;">
            Умный дневник для школьника
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Auth.py", label="→ Войти или зарегистрироваться")
else:
    user = st.session_state.get("user", {})
    st.markdown(f"""
    <div style="font-family:'DM Serif Display',serif;font-size:2rem;
                color:#e8eaf0;margin-bottom:8px;">
        Добро пожаловать, {user.get('nickname','')}!
    </div>
    <p style="color:#8890a6;font-size:13px;">Выбери раздел в боковом меню.</p>
    """, unsafe_allow_html=True)