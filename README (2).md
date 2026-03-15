import streamlit as st

st.title("👥 Группы")

# Получить список групп
response = api_request("GET", "/groups/")

# Вкладки
tab_list, tab_create = st.tabs(["Мои группы", "Создать группу"])

with tab_create:
    st.subheader("Создать новую группу")
    
    with st.form("create_group_form"):
        group_name = st.text_input("Название группы")
        group_description = st.text_area("Описание", height=100)
        
        submitted = st.form_submit_button("Создать")
        
        if submitted and group_name:
            response = api_request("POST", "/groups/", json={
                "name": group_name,
                "description": group_description
            })
            
            if response and response.status_code == 200:
                st.success("Группа создана!")
                st.rerun()
            elif response:
                st.error(f"Ошибка: {response.text}")

with tab_list:
    if response and response.status_code == 200:
        groups = response.json()
        
        if groups:
            st.write(f"Найдено групп: {len(groups)}")
            
            for group in groups:
                with st.expander(f"📁 {group['name']} ({group.get('members_count', 0)} участников)"):
                    st.write(group.get("description", "Нет описания"))
                    
                    # Получить участников
                    members_response = api_request("GET", f"/groups/{group['id']}/members")
                    if members_response and members_response.status_code == 200:
                        members = members_response.json()
                        st.write("**Участники:**")
                        for member in members:
                            role_emoji = "👑" if member["role"] == "admin" else "👤"
                            st.write(f"{role_emoji} User #{member['user_id']} ({member['role']})")
                    
                    # Действия
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"Редактировать", key=f"edit_group_{group['id']}"):
                            st.session_state.edit_group_id = group["id"]
                            st.session_state.edit_group_name = group["name"]
                            st.session_state.edit_group_desc = group.get("description", "")
                            st.rerun()
                    with col2:
                        if st.button(f"Добавить участника", key=f"add_member_{group['id']}"):
                            st.session_state.add_member_group_id = group["id"]
                            st.rerun()
                    with col3:
                        if st.button(f"Удалить группу", key=f"del_group_{group['id']}"):
                            response = api_request("DELETE", f"/groups/{group['id']}")
                            if response and response.status_code == 204:
                                st.success("Группа удалена!")
                                st.rerun()
                            elif response:
                                st.error(f"Ошибка: {response.text}")
        else:
            st.info("Вы не состоите в группах")
    elif response:
        st.error(f"Ошибка: {response.text}")

# Редактирование группы
if "edit_group_id" in st.session_state:
    st.divider()
    st.subheader("Редактировать группу")
    
    with st.form("edit_group_form"):
        new_name = st.text_input("Название", value=st.session_state.edit_group_name)
        new_desc = st.text_area("Описание", value=st.session_state.edit_group_desc)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Сохранить")
        with col2:
            cancel = st.form_submit_button("Отмена")
        
        if submitted:
            response = api_request("PUT", f"/groups/{st.session_state.edit_group_id}", json={
                "name": new_name,
                "description": new_desc
            })
            if response and response.status_code == 200:
                del st.session_state.edit_group_id
                st.success("Группа обновлена!")
                st.rerun()
            elif response:
                st.error(f"Ошибка: {response.text}")
        
        if cancel:
            del st.session_state.edit_group_id
            st.rerun()

# Добавление участника
if "add_member_group_id" in st.session_state:
    st.divider()
    st.subheader("Добавить участника в группу")
    
    with st.form("add_member_form"):
        member_login = st.text_input("Логин пользователя")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Добавить")
        with col2:
            cancel = st.form_submit_button("Отмена")
        
        if submitted and member_login:
            response = api_request("POST", f"/groups/{st.session_state.add_member_group_id}/members", json={
                "user_login": member_login
            })
            if response and response.status_code == 200:
                del st.session_state.add_member_group_id
                st.success("Участник добавлен!")
                st.rerun()
            elif response:
                st.error(f"Ошибка: {response.text}")
        
        if cancel:
            del st.session_state.add_member_group_id
            st.rerun()
