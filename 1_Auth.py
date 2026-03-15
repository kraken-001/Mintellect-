"""
Страница 4 — Заметки.
Список с фильтрами, создание, редактирование, удаление, вложения.
"""
import streamlit as st
import sys, os
from datetime import datetime, date
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui_helpers import inject_css, require_auth, sidebar_user_info, DAYS
import api_client as api

st.set_page_config(page_title="Заметки · Mintellect", page_icon="📝", layout="wide")
inject_css()
sidebar_user_info()
token, user = require_auth()

st.markdown("""
<div class="mint-hero">
    <h1>📝 Заметки</h1>
    <p>Записи к урокам и свободные мысли</p>
</div>
""", unsafe_allow_html=True)

# ── ЗАГРУЗКА РАСПИСАНИЯ ───────────────────────────────────────────────────────
try:
    schedules = api.get_schedule(token)
except Exception:
    schedules = []

schedule_map = {s["id"]: f"{DAYS[s['day_of_week']]} — {s['subject']}" for s in schedules}

# ── SIDEBAR ФИЛЬТРЫ ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Фильтры")

    filter_mode = st.radio("Показать", ["Все", "По дате", "По уроку", "Диапазон дат"],
                           label_visibility="collapsed")

    filter_date      = None
    filter_start     = None
    filter_end       = None
    filter_sched_id  = None

    if filter_mode == "По дате":
        filter_date = st.date_input("Дата", value=date.today())
    elif filter_mode == "По уроку":
        if schedule_map:
            sched_labels = {v: k for k, v in schedule_map.items()}
            sel_label    = st.selectbox("Урок", list(sched_labels.keys()))
            filter_sched_id = sched_labels[sel_label]
        else:
            st.caption("Расписание пустое")
    elif filter_mode == "Диапазон дат":
        filter_start = st.date_input("С",  value=date.today())
        filter_end   = st.date_input("По", value=date.today())

    st.divider()
    if st.button("+ Новая заметка", type="primary", use_container_width=True):
        st.session_state.pop("edit_note_id", None)
        st.session_state["show_editor"] = True

# ── ЗАГРУЗКА ЗАМЕТОК ──────────────────────────────────────────────────────────
try:
    if filter_mode == "По дате" and filter_date:
        notes = api.get_notes_by_date(token, filter_date.strftime("%Y-%m-%d"))
    elif filter_mode == "Диапазон дат":
        notes = api.get_notes(token,
                              start_date=filter_start.strftime("%Y-%m-%d") if filter_start else None,
                              end_date=filter_end.strftime("%Y-%m-%d")   if filter_end   else None)
    elif filter_mode == "По уроку" and filter_sched_id:
        notes = api.get_notes(token, schedule_id=filter_sched_id)
    else:
        notes = api.get_notes(token)
except Exception as e:
    st.error(f"Ошибка загрузки заметок: {e}")
    notes = []

# ── LAYOUT ────────────────────────────────────────────────────────────────────
list_col, editor_col = st.columns([2, 3], gap="large")

# ── СПИСОК ЗАМЕТОК ────────────────────────────────────────────────────────────
with list_col:
    st.markdown(f"**{len(notes)} заметок**")

    if not notes:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">📓</div>
            <div>Заметок не найдено</div>
        </div>""", unsafe_allow_html=True)
    else:
        for note in notes:
            snippet = note.get("content", "")[:100]
            sched_label = schedule_map.get(note.get("schedule_id"), "")

            is_selected = st.session_state.get("edit_note_id") == note["id"]
            border_color = "#e8c76a44" if is_selected else "#232736"

            st.markdown(f"""
            <div class="note-card" style="border-color:{border_color}">
                <div class="note-card-title">{note['title']}</div>
                <div class="note-card-meta">{note.get('date','')}
                    {' · ' + sched_label if sched_label else ''}
                </div>
                <div class="note-card-body">{snippet}{'…' if len(snippet)==100 else ''}</div>
            </div>
            """, unsafe_allow_html=True)

            btn_col1, btn_col2 = st.columns([1, 1])
            with btn_col1:
                if st.button("Открыть", key=f"open_{note['id']}", use_container_width=True):
                    st.session_state["edit_note_id"] = note["id"]
                    st.session_state["show_editor"]  = True
                    st.rerun()
            with btn_col2:
                if st.button("Удалить", key=f"del_{note['id']}",
                             use_container_width=True, type="secondary"):
                    if api.delete_note(token, note["id"]):
                        if st.session_state.get("edit_note_id") == note["id"]:
                            st.session_state.pop("edit_note_id", None)
                        st.success("Заметка удалена")
                        st.rerun()

# ── РЕДАКТОР ──────────────────────────────────────────────────────────────────
with editor_col:
    show_editor = st.session_state.get("show_editor", False)
    edit_id     = st.session_state.get("edit_note_id")

    if not show_editor and edit_id is None:
        st.markdown("""
        <div class="empty-state" style="margin-top:60px;">
            <div class="empty-icon">✍️</div>
            <div>Выберите заметку или нажмите «Новая заметка»</div>
        </div>""", unsafe_allow_html=True)
    else:
        # Загрузить существующую
        existing = None
        if edit_id:
            try:
                existing = api.get_note(token, edit_id)
            except Exception:
                st.error("Заметка не найдена")
                existing = None

        title_mode = "✏️ Редактировать заметку" if existing else "✨ Новая заметка"
        st.markdown(f"#### {title_mode}")

        with st.form("note_editor_form", clear_on_submit=False):
            note_title = st.text_input(
                "Заголовок",
                value=existing["title"] if existing else "",
                placeholder="Заголовок заметки..."
            )

            c1, c2 = st.columns([1, 2])
            with c1:
                default_date = (
                    date.fromisoformat(existing["date"])
                    if existing and existing.get("date") else date.today()
                )
                note_date = st.date_input("Дата", value=default_date)
            with c2:
                sched_options = {"Без урока": None}
                sched_options.update({v: k for k, v in schedule_map.items()})
                current_sched_label = (
                    schedule_map.get(existing.get("schedule_id"), "Без урока")
                    if existing else "Без урока"
                )
                sel_sched = st.selectbox(
                    "Урок (необязательно)",
                    list(sched_options.keys()),
                    index=list(sched_options.keys()).index(current_sched_label)
                    if current_sched_label in sched_options else 0
                )

            note_content = st.text_area(
                "Содержание",
                value=existing["content"] if existing else "",
                height=260,
                placeholder="Начни писать..."
            )

            fcol1, fcol2 = st.columns([2, 1])
            with fcol1:
                save_btn = st.form_submit_button(
                    "💾 Сохранить" if existing else "✨ Создать",
                    type="primary", use_container_width=True
                )
            with fcol2:
                cancel_btn = st.form_submit_button("Отмена", use_container_width=True)

        if cancel_btn:
            st.session_state.pop("edit_note_id", None)
            st.session_state["show_editor"] = False
            st.rerun()

        if save_btn:
            if not note_title.strip():
                st.error("Введите заголовок")
            elif not note_content.strip():
                st.error("Введите содержание")
            else:
                sched_id = sched_options.get(sel_sched)
                try:
                    if existing:
                        api.update_note(token, existing["id"],
                                        note_title, note_content,
                                        note_date.strftime("%Y-%m-%d"), sched_id)
                        st.success("Заметка обновлена!")
                    else:
                        new_note = api.create_note(token, note_title, note_content,
                                                   note_date.strftime("%Y-%m-%d"), sched_id)
                        st.session_state["edit_note_id"] = new_note["id"]
                        st.success("Заметка создана!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

        # ── ВЛОЖЕНИЯ ──────────────────────────────────────────────────────────
        if existing:
            st.markdown("---")
            st.markdown("##### 📎 Вложения")

            try:
                attachments = api.get_attachments(token, existing["id"])
            except Exception:
                attachments = []

            if attachments:
                for att in attachments:
                    att_col1, att_col2, att_col3 = st.columns([3, 1, 1])
                    with att_col1:
                        st.markdown(f"""
                        <div class="attach-chip">📎 {att.get('filename', f'Файл #{att["id"]}')}</div>
                        """, unsafe_allow_html=True)
                    with att_col2:
                        try:
                            file_bytes = api.download_attachment(token, existing["id"], att["id"])
                            st.download_button(
                                "⬇",
                                data=file_bytes,
                                file_name=att.get("filename", "file"),
                                key=f"dl_{att['id']}"
                            )
                        except Exception:
                            st.caption("—")
                    with att_col3:
                        if st.button("✕", key=f"delatt_{att['id']}"):
                            if api.delete_attachment(token, existing["id"], att["id"]):
                                st.rerun()
            else:
                st.caption("Нет вложений")

            uploaded = st.file_uploader(
                "Прикрепить файл",
                key=f"upload_{existing['id']}",
                label_visibility="collapsed"
            )
            if uploaded:
                try:
                    api.upload_attachment(
                        token, existing["id"],
                        uploaded.read(), uploaded.name, uploaded.type
                    )
                    st.success(f"Файл «{uploaded.name}» прикреплён!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
