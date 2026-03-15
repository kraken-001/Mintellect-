"""
Страница 6 — Настройки / профиль.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui_helpers import inject_css, require_auth, sidebar_user_info
import api_client as api

st.set_page_config(page_title="Настройки · Mintellect", page_icon="⚙️", layout="centered")
inject_css()
sidebar_user_info()
token, user = require_auth()

st.markdown("""
<div class="mint-hero">
    <h1>⚙️ Настройки</h1>
    <p>Информация об аккаунте и конфигурация</p>
</div>
""", unsafe_allow_html=True)

# ── ПРОФИЛЬ ───────────────────────────────────────────────────────────────────
st.markdown("#### Профиль")

col1, col2 = st.columns([1, 3])
with col1:
    st.markdown(f"""
    <div style="width:80px;height:80px;background:#e8c76a;border-radius:50%;
                display:flex;align-items:center;justify-content:center;
                font-family:'DM Serif Display',serif;font-size:2rem;color:#0d0f14;
                font-weight:700;">
        {user.get('nickname','?')[0].upper()}
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="padding:8px 0">
        <div style="font-size:1.4rem;font-weight:600;margin-bottom:4px">
            {user.get('nickname','—')}
        </div>
        <div style="color:#8890a6;font-size:13px">ID: {user.get('id','?')}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── СТАТИСТИКА ────────────────────────────────────────────────────────────────
st.markdown("#### Статистика")

try:
    notes    = api.get_notes(token)
    schedule = api.get_schedule(token)
    groups   = api.get_groups(token)
    n_notes  = len(notes)
    n_sched  = len(schedule)
    n_groups = len(groups)
except Exception:
    n_notes = n_sched = n_groups = 0

s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_notes}</div>
        <div class="metric-label">заметок</div>
    </div>""", unsafe_allow_html=True)
with s2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{n_sched}</div>
        <div class="metric-label">уроков</div>
    </div>""", unsafe_allow_html=True)
with s3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:#7b9cff">{n_groups}</div>
        <div class="metric-label">групп</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ── API НАСТРОЙКИ ─────────────────────────────────────────────────────────────
st.markdown("#### Подключение к серверу")

import api_client
current_url = api_client.BASE_URL

new_url = st.text_input("URL бэкенда", value=current_url,
                         help="Адрес FastAPI сервера (без /api)")

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("Сохранить URL", type="primary"):
        api_client.BASE_URL = new_url.rstrip("/") + "/api"
        st.success("URL обновлён!")

with col_b:
    if st.button("Проверить соединение"):
        import requests
        try:
            r = requests.get(new_url.rstrip("/").replace("/api", "") + "/api/health", timeout=3)
            if r.ok:
                st.success(f"✅ Сервер доступен: {r.json().get('status','ok')}")
            else:
                st.error(f"Сервер ответил {r.status_code}")
        except Exception as e:
            st.error(f"Недоступен: {e}")

st.divider()

# ── ВЫЙТИ ─────────────────────────────────────────────────────────────────────
st.markdown("#### Аккаунт")
if st.button("🚪 Выйти из аккаунта", type="secondary"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Вы вышли из аккаунта")
    st.page_link("pages/1_Вход.py", label="→ Войти снова")
