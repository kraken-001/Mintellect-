import streamlit as st
from datetime import time

st.title("📅 Расписание")

# Дни недели
DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

# Получить расписание
response = api_request("GET", "/schedule/my")
if response and response.status_code == 200:
    schedule = response.json()
    
    # Группировка по дням
    by_day = {i: [] for i in range(7)}
    for lesson in schedule:
        by_day[lesson["day_of_week"]].append(lesson)
    
    # Показ расписания по дням
    tab_view, tab_edit = st.tabs(["Просмотр", "Редактирование"])
    
    with tab_view:
        selected_day = st.selectbox("День недели", range(7), format_func=lambda x: DAYS[x])
        
        lessons = by_day[selected_day]
        if lessons:
            for lesson in lessons:
                st.write(f"**{lesson['subject']}** — {lesson['start_time'][:5]} - {lesson['end_time'][:5]}")
        else:
            st.info("Нет уроков в этот день")
    
    with tab_edit:
        st.subheader("Добавить предмет")
        
        with st.form("add_lesson_form"):
            new_day = st.selectbox("День", range(7), format_func=lambda x: DAYS[x], key="new_day")
            new_subject = st.text_input("Предмет", key="new_subject")
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("Начало", time(9, 0), key="start_time")
            with col2:
                end_time = st.time_input("Конец", time(10, 30), key="end_time")
            
            submitted = st.form_submit_button("Добавить")
            
            if submitted and new_subject:
                # Форматирование времени
                start_str = start_time.strftime("%H:%M:%S")
                end_str = end_time.strftime("%H:%M:%S")
                
                response = api_request("POST", "/schedule/", json={
                    "day_of_week": new_day,
                    "subject": new_subject,
                    "start_time": start_str,
                    "end_time": end_str
                })
                
                if response and response.status_code == 200:
                    st.success("Предмет добавлен!")
                    st.rerun()
                elif response:
                    st.error(f"Ошибка: {response.text}")
        
        st.divider()
        
        # Удаление предмета
        st.subheader("Удалить предмет")
        if schedule:
            lesson_options = [f"{DAYS[l['day_of_week']]}: {l['subject']} ({l['start_time'][:5]}-{l['end_time'][:5]})" for l in schedule]
            selected_lesson = st.selectbox("Выберите предмет", range(len(lesson_options)), format_func=lambda x: lesson_options[x])
            
            if st.button("Удалить предмет"):
                lesson_id = schedule[selected_lesson]["id"]
                response = api_request("DELETE", f"/schedule/{lesson_id}")
                if response and response.status_code == 200:
                    st.success("Предмет удалён!")
                    st.rerun()
                elif response:
                    st.error(f"Ошибка: {response.text}")
            
            st.divider()
            
            if st.button("🗑️ Очистить всё расписание", type="primary"):
                response = api_request("DELETE", "/schedule/")
                if response and response.status_code == 204:
                    st.success("Расписание очищено!")
                    st.rerun()
                elif response:
                    st.error(f"Ошибка: {response.text}")
        else:
            st.info("Расписание пустое")

elif response is None:
    st.error("Не удалось загрузить расписание")
