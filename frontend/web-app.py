import streamlit as st
st.title("Directed Graph Task Scheduling")
st.header("Enter Tasks and Priorities")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

with  st.form("task_form", clear_on_submit = True):
    task_name = st.text_input("Task Name")
    priority = st.selectbox("Priority", ["Level 1", "Level 2", "Level 3", "Level 4"])
    submit = st.form_submit_button("Add Task")

    if submit and task_name:
        st.session_state.tasks.append({"task": task_name, "priority": priority})
        st.success(f"Added: {task_name} ({priority} priority)")


st.subheader("List of Tasks Added")
for t in st.session_state.tasks:
    st.write(f"-{t['task']} | Priority: {t['priority']}")