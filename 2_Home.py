"""
Страница 5 — Группы.
Создание, просмотр участников, групповые заметки.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui_helpers import inject_css, require_auth, sidebar_user_info
import api_client as api

st.set_page_config(page_title="Группы · Mintellect", page_icon="👥", layout="wide")
inject_css()
sidebar_user_info()
token, user = require_auth()

st.markdown("""
<div class="mint-hero">
    <h1>👥 Группы</h1>
    <p>Совместные заметки с одноклассниками</p>
</div>
""", unsafe_allow_html=True)

# ── ЗАГРУЗКА ГРУПП ────────────────────────────────────────────────────────────
try:
    groups = api.get_groups(token)
except Exception as e:
    st.error(f"Ошибка загрузки групп: {e}")
    groups = []

# ── LAYOUT ────────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 2], gap="large")

# ── СПИСОК ГРУПП ──────────────────────────────────────────────────────────────
with left_col:
    st.markdown("#### Мои группы")

    # Создать группу
    with st.expander("➕ Создать группу"):
        with st.form("create_group_form", clear_on_submit=True):
            new_name = st.text_input("Название группы", placeholder="Класс 10А")
            new_desc = st.text_area("Описание", placeholder="Описание группы...", height=80)
            if st.form_submit_button("Создать", type="primary", use_container_width=True):
                if not new_name.strip():
                    st.error("Введите название")
                else:
                    try:
                        api.create_group(token, new_name, new_desc)
                        st.success("Группа создана!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

    if not groups:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">👥</div>
            <div>Групп пока нет</div>
        </div>""", unsafe_allow_html=True)
    else:
        for g in groups:
            is_selected = st.session_state.get("selected_group_id") == g["id"]
            border = "#e8c76a44" if is_selected else "#232736"

            st.markdown(f"""
            <div class="group-card" style="border-color:{border}">
                <div class="group-card-name">{g['name']}</div>
                <div class="group-card-desc">{g.get('description','')[:80]}</div>
            </div>
            """, unsafe_allow_html=True)

            btn1, btn2 = st.columns([1, 1])
            with btn1:
                if st.button("Открыть", key=f"sel_{g['id']}", use_container_width=True):
                    st.session_state["selected_group_id"] = g["id"]
                    st.rerun()
            with btn2:
                if st.button("Удалить", key=f"delg_{g['id']}",
                             use_container_width=True, type="secondary"):
                    if api.delete_group(token, g["id"]):
                        if st.session_state.get("selected_group_id") == g["id"]:
                            st.session_state.pop("selected_group_id", None)
                        st.success("Группа удалена")
                        st.rerun()

# ── ДЕТАЛИ ГРУППЫ ─────────────────────────────────────────────────────────────
with right_col:
    sel_id = st.session_state.get("selected_group_id")

    if not sel_id:
        st.markdown("""
        <div class="empty-state" style="margin-top:60px;">
            <div class="empty-icon">👈</div>
            <div>Выберите группу слева</div>
        </div>""", unsafe_allow_html=True)
    else:
        try:
            group = api.get_group(token, sel_id)
        except Exception:
            st.error("Не удалось загрузить группу")
            st.stop()

        # Заголовок группы
        g_col1, g_col2 = st.columns([3, 1])
        with g_col1:
            st.markdown(f"### {group['name']}")
            if group.get("description"):
                st.caption(group["description"])
        with g_col2:
            if st.button("⚙️ Редактировать", use_container_width=True):
                st.session_state["editing_group"] = sel_id

        # Форма редактирования
        if st.session_state.get("editing_group") == sel_id:
            with st.form("edit_group_form"):
                upd_name = st.text_input("Название", value=group["name"])
                upd_desc = st.text_area("Описание", value=group.get("description",""), height=80)
                col_s, col_c = st.columns([1,1])
                with col_s:
                    if st.form_submit_button("Сохранить", type="primary"):
                        try:
                            api.update_group(token, sel_id, upd_name, upd_desc)
                            st.session_state.pop("editing_group", None)
                            st.success("Обновлено!")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                with col_c:
                    if st.form_submit_button("Отмена"):
                        st.session_state.pop("editing_group", None)
                        st.rerun()

        st.divider()

        # ── УЧАСТНИКИ ─────────────────────────────────────────────────────────
        members_tab, notes_tab = st.tabs(["👤 Участники", "📝 Заметки группы"])

        with members_tab:
            try:
                members = api.get_members(token, sel_id)
            except Exception:
                members = []

            # Добавить участника
            with st.form("add_member_form", clear_on_submit=True):
                mc1, mc2 = st.columns([3, 1])
                with mc1:
                    member_login = st.text_input("Логин участника",
                                                 placeholder="user_login",
                                                 label_visibility="collapsed")
                with mc2:
                    add_m = st.form_submit_button("Добавить", type="primary",
                                                  use_container_width=True)
            if add_m:
                if not member_login.strip():
                    st.error("Введите логин")
                else:
                    try:
                        api.add_member(token, sel_id, member_login)
                        st.success(f"Участник «{member_login}» добавлен!")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

            if not members:
                st.info("В группе пока нет участников")
            else:
                for m in members:
                    mcol1, mcol2 = st.columns([3, 1])
                    with mcol1:
                        is_me = m.get("id") == user.get("id")
                        st.markdown(f"""
                        <div style="padding:10px 14px;background:#13161d;
                                    border:1px solid #232736;border-radius:8px;
                                    display:flex;align-items:center;gap:10px;">
                            <div style="width:30px;height:30px;background:{'#e8c76a' if is_me else '#232736'};
                                        border-radius:50%;display:flex;align-items:center;
                                        justify-content:center;font-size:13px;font-weight:600;
                                        color:{'#0d0f14' if is_me else '#8890a6'};">
                                {m.get('nickname','?')[0].upper()}
                            </div>
                            <div>
                                <div style="font-size:13px;font-weight:500">
                                    {m.get('nickname','—')}{' (вы)' if is_me else ''}
                                </div>
                                <div style="font-size:11px;color:#8890a6">
                                    @{m.get('login','—')}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with mcol2:
                        if not is_me:
                            if st.button("✕", key=f"rem_{m['id']}_{sel_id}",
                                         use_container_width=True):
                                if api.remove_member(token, sel_id, m["id"]):
                                    st.success("Участник удалён")
                                    st.rerun()
                        else:
                            st.write("")  # spacer

        with notes_tab:
            try:
                group_notes = api.get_group_notes(token, sel_id)
            except Exception as e:
                st.error(f"Ошибка загрузки заметок: {e}")
                group_notes = []

            if not group_notes:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <div>В группе пока нет заметок</div>
                </div>""", unsafe_allow_html=True)
            else:
                for note in group_notes:
                    snippet = note.get("content", "")[:120]
                    with st.expander(f"**{note['title']}** · {note.get('date','')}"):
                        st.write(note.get("content",""))
                        author = note.get("author_nickname", note.get("user_id","?"))
                        st.caption(f"Автор: {author}")
