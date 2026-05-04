import streamlit as st
import pandas as pd

from backend.graph_builder import build_graph
from backend.topological_sort_bfs import topo_sort_bfs
from backend.topological_sort_dfs import topo_sort_dfs
from backend.priority_scheduler import schedule
from backend.visualizer import draw_graph



def adjacency_matrix(tasks, graph):
    nodes = [t["task"] for t in tasks]
    n = len(nodes)

    index = {node: i for i, node in enumerate(nodes)}
    matrix = [[0]*n for _ in range(n)]

    for u in graph:
        for v in graph[u]:
            matrix[index[u]][index[v]] = 1

    return nodes, matrix



st.title("Directed Graph Task Scheduling")


if "tasks" not in st.session_state:
    st.session_state.tasks = []



with st.form("task_form", clear_on_submit=True):
    task_name = st.text_input("Task Name")

    priority = st.selectbox(
        "Priority",
        ["Level 1", "Level 2", "Level 3"]
    )

    existing_tasks = [t["task"] for t in st.session_state.tasks]

    depends_on = st.multiselect(
        "Depends on",
        existing_tasks
    )

    submitted = st.form_submit_button("Add Task")

    if submitted and task_name:
        if task_name in existing_tasks:
            st.warning("Task already exists!")
        else:
            st.session_state.tasks.append({
                "task": task_name,
                "priority": priority,
                "depends_on": depends_on
            })



if st.button("Clear Tasks"):
    st.session_state.tasks = []



st.subheader("Tasks")

for i, t in enumerate(st.session_state.tasks):
    st.write(f"### {t['task']}")

    
    new_priority = st.selectbox(
        f"Priority for {t['task']}",
        ["Level 1", "Level 2", "Level 3"],
        index=["Level 1", "Level 2", "Level 3"].index(t["priority"]),
        key=f"priority_{i}"
    )

    
    existing_tasks = [
        task["task"] for task in st.session_state.tasks
        if task["task"] != t["task"]
    ]

    new_deps = st.multiselect(
        f"Depends on for {t['task']}",
        existing_tasks,
        default=t["depends_on"],
        key=f"deps_{i}"
    )

    
    t["priority"] = new_priority
    t["depends_on"] = new_deps



algo = st.selectbox(
    "Choose Algorithm",
    ["BFS", "DFS", "Priority Scheduling"]
)



graph = build_graph(st.session_state.tasks)



if st.button("Run Scheduler"):
    if algo == "BFS":
        result = topo_sort_bfs(st.session_state.tasks, graph)

    elif algo == "DFS":
        result = topo_sort_dfs(st.session_state.tasks, graph)

    else:
        result = schedule(st.session_state.tasks, graph)

    if result is None:
        st.error("Cycle detected")
    else:
        st.subheader("Execution Order")
        for i, task in enumerate(result, 1):
            st.write(f"{i}. {task}")



if st.button("Adjacency Matrix"):
    nodes, matrix = adjacency_matrix(st.session_state.tasks, graph)

    df = pd.DataFrame(matrix, index=nodes, columns=nodes)

    st.subheader("Adjacency Matrix")
    st.caption("Rows = source, Columns = dependent")

    if all(all(cell == 0 for cell in row) for row in matrix):
        st.info("No dependencies → Graph has no edges")

    st.dataframe(df)



if st.button("Visualize Graph"):
    fig = draw_graph(st.session_state.tasks, graph)
    st.pyplot(fig)