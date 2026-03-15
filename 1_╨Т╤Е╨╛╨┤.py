"""
Страница групп.
"""
import streamlit as st
from api_client import get_groups, create_group, update_group, delete_group, get_members, add_member
from ui_helpers import inject_css, page_header, require_auth

inject_css()
token, user = require_auth()
page_header("Группы", "Управляй группами и участниками")

# Tabs
tab_list, tab_create = st.tabs(["Мои группы", "Создать группу"])

with tab_create:
    with st.form("create_group"):
        name = st.text_input("Название группы")
        description = st.text_area("Описание")
        submit = st.form_submit_button("Создать", use_container_width=True)
        
        if submit:
            if not name:
                st.error("Введи название")
            else:
                try:
                    create_group(token, name, description)
                    st.success("Группа создана!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with tab_list:
    try:
        groups = get_groups(token)
    except Exception as e:
        st.error(f"Ошибка: {e}")
        groups = []
    
    if groups:
        for group in groups:
            with st.expander(f"📁 {group['name']} ({group.get('members_count', 0)} участников)"):
                st.write(group.get("description", "Нет описания"))
                
                # Участники
                try:
                    members = get_members(token, group["id"])
                    st.write("**Участники:**")
                    for m in members:
                        role = "👑" if m["role"] == "admin" else "👤"
                        st.write(f"{role} User #{m['user_id']}")
                except:
                    pass
                
                # Действия
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Редактировать", key=f"edit_g_{group['id']}"):
                        st.session_state.edit_group = group
                        st.rerun()
                with col2:
                    if st.button("Удалить", key=f"del_g_{group['id']}"):
                        try:
                            delete_group(token, group["id"])
                            st.success("Удалено!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Ошибка: {e}")
                with col3:
                    if st.button("Добавить участника", key=f"add_m_{group['id']}"):
                        st.session_state.add_member_group = group["id"]
                        st.rerun()
    else:
        st.info("Ты не состоишь в группах")

# Редактирование группы
if "edit_group" in st.session_state:
    st.divider()
    group = st.session_state.edit_group
    with st.form("edit_group"):
        name = st.text_input("Название", value=group["name"])
        description = st.text_area("Описание", value=group.get("description", ""))
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Сохранить", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Отмена", use_container_width=True)
        
        if submit:
            try:
                update_group(token, group["id"], name, description)
                del st.session_state.edit_group
                st.success("Сохранено!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка: {e}")
        
        if cancel:
            del st.session_state.edit_group
            st.rerun()

# Добавление участника
if "add_member_group" in st.session_state:
    st.divider()
    with st.form("add_member"):
        user_login = st.text_input("Логин пользователя")
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Добавить", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Отмена", use_container_width=True)
        
        if submit and user_login:
            try:
                add_member(token, st.session_state.add_member_group, user_login)
                del st.session_state.add_member_group
                st.success("Добавлен!")
                st.rerun()
            except Exception as e:
                st.error(f"Ошибка: {e}")
        
        if cancel:
            del st.session_state.add_member_group
            st.rerun()