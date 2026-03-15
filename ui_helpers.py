import streamlit as st
from datetime import date, timedelta

st.title("📝 Заметки")

# Получить расписание для выбора
schedule_response = api_request("GET", "/schedule/my")
schedule = schedule_response.json() if schedule_response and schedule_response.status_code == 200 else []

# Вкладки
tab_list, tab_create = st.tabs(["Список заметок", "Создать заметку"])

with tab_list:
    # Фильтры
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_date = st.date_input("Дата (от)", value=None)
    with col2:
        filter_date_end = st.date_input("Дата (до)", value=None)
    with col3:
        schedule_options = ["Все"] + [s["subject"] for s in schedule]
        filter_subject = st.selectbox("Предмет", schedule_options)
    
    # Параметры запроса
    params = {}
    if filter_date:
        params["start_date"] = filter_date.isoformat()
    if filter_date_end:
        params["end_date"] = filter_date_end.isoformat()
    if filter_subject != "Все":
        schedule_id = next((s["id"] for s in schedule if s["subject"] == filter_subject), None)
        if schedule_id:
            params["schedule_id"] = schedule_id
    
    # Получение заметок
    response = api_request("GET", "/notes/", params=params if params else None)
    
    if response and response.status_code == 200:
        notes = response.json()
        
        st.write(f"Найдено заметок: {len(notes)}")
        
        if notes:
            for note in notes:
                with st.expander(f"📌 {note['title']} ({note['date']})"):
                    st.write(note["content"])
                    
                    if note.get("schedule_id"):
                        lesson = next((s for s in schedule if s["id"] == note["schedule_id"]), None)
                        if lesson:
                            st.caption(f"📚 {lesson['subject']}")
                    
                    # Вложения
                    if note.get("attachments"):
                        st.write("**Вложения:**")
                        for att in note["attachments"]:
                            st.write(f"📎 {att['file_name']}")
                    
                    # Кнопки действий
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Редактировать", key=f"edit_{note['id']}"):
                            st.session_state.edit_note_id = note["id"]
                            st.session_state.edit_note_title = note["title"]
                            st.session_state.edit_note_content = note["content"]
                            st.rerun()
                    with col2:
                        if st.button(f"Удалить", key=f"del_{note['id']}"):
                            response = api_request("DELETE", f"/notes/{note['id']}")
                            if response and response.status_code == 200:
                                st.success("Заметка удалена!")
                                st.rerun()
                            elif response:
                                st.error(f"Ошибка: {response.text}")
        else:
            st.info("Заметок не найдено")
    elif response:
        st.error(f"Ошибка: {response.text}")

with tab_create:
    st.subheader("Новая заметка")
    
    # Проверка режима редактирования
    if "edit_note_id" in st.session_state:
        st.warning(f"Редактирование заметки #{st.session_state.edit_note_id}")
        note_title = st.text_input("Заголовок", value=st.session_state.edit_note_title, key="edit_title")
        note_content = st.text_area("Содержание", value=st.session_state.edit_note_content, key="edit_content")
        
        if st.button("Сохранить изменения"):
            response = api_request("PUT", f"/notes/{st.session_state.edit_note_id}", json={
                "title": note_title,
                "content": note_content,
                "date": date.today().isoformat()
            })
            if response and response.status_code == 200:
                del st.session_state.edit_note_id
                del st.session_state.edit_note_title
                del st.session_state.edit_note_content
                st.success("Заметка обновлена!")
                st.rerun()
            elif response:
                st.error(f"Ошибка: {response.text}")
        
        if st.button("Отмена"):
            del st.session_state.edit_note_id
            st.rerun()
    else:
        # Создание новой заметки
        with st.form("create_note_form"):
            note_title = st.text_input("Заголовок", key="new_title")
            note_content = st.text_area("Содержание", key="new_content")
            note_date = st.date_input("Дата", value=date.today())
            
            schedule_options = ["Без урока"] + [s["subject"] for s in schedule]
            selected_subject = st.selectbox("Связать с уроком", schedule_options)
            
            schedule_id = None
            if selected_subject != "Без урока":
                schedule_id = next((s["id"] for s in schedule if s["subject"] == selected_subject), None)
            
            visibility = st.radio("Видимость", ["private", "group"], format_func=lambda x: "Личная" if x == "private" else "Групповая")
            
            group_id = None
            if visibility == "group":
                groups_response = api_request("GET", "/groups/")
                if groups_response and groups_response.status_code == 200:
                    groups = groups_response.json()
                    if groups:
                        group_options = [g["name"] for g in groups]
                        selected_group = st.selectbox("Группа", group_options)
                        group_id = next((g["id"] for g in groups if g["name"] == selected_group), None)
                    else:
                        st.warning("Нет доступных групп")
                else:
                    st.warning("Не удалось загрузить группы")
            
            submitted = st.form_submit_button("Создать заметку")
            
            if submitted and note_title and note_content:
                payload = {
                    "title": note_title,
                    "content": note_content,
                    "date": note_date.isoformat(),
                    "visibility": visibility
                }
                if schedule_id:
                    payload["schedule_id"] = schedule_id
                if group_id:
                    payload["group_id"] = group_id
                
                response = api_request("POST", "/notes/", json=payload)
                
                if response and response.status_code == 200:
                    st.success("Заметка создана!")
                    st.rerun()
                elif response:
                    st.error(f"Ошибка: {response.text}")
