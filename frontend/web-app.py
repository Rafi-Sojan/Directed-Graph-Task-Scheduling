import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from backend.analysis import ALGORITHM_DESIGN, TEST_CASES, run_analysis
from backend.cycle_detector import find_cycle
from backend.graph_builder import build_graph
from backend.topological_sort_bfs import topo_sort_bfs
from backend.topological_sort_dfs import topo_sort_dfs
from backend.visualizer import draw_graph


SAMPLE_TASKS = [
    {"task": "Collect Requirements", "depends_on": []},
    {"task": "Design DAG", "depends_on": ["Collect Requirements"]},
    {"task": "Implement Scheduler", "depends_on": ["Design DAG"]},
    {"task": "Write Tests", "depends_on": ["Implement Scheduler"]},
    {"task": "Prepare Report", "depends_on": ["Design DAG"]},
]


def normalize_task_name(name):
    return " ".join(name.strip().split())


def adjacency_matrix(tasks, graph):
    nodes = [task["task"] for task in tasks]
    index = {node: i for i, node in enumerate(nodes)}
    matrix = [[0 for _ in nodes] for _ in nodes]

    for source, neighbours in graph.items():
        for target in neighbours:
            matrix[index[source]][index[target]] = 1

    return nodes, matrix


def remove_task(task_name):
    st.session_state.tasks = [
        task for task in st.session_state.tasks if task["task"] != task_name
    ]
    for task in st.session_state.tasks:
        task["depends_on"] = [
            dep for dep in task.get("depends_on", []) if dep != task_name
        ]


def run_scheduler(algorithm, tasks, graph):
    if algorithm == "BFS":
        return topo_sort_bfs(tasks, graph)
    return topo_sort_dfs(tasks, graph)


def count_ready_tasks(graph):
    blocked_tasks = {
        target for neighbours in graph.values() for target in neighbours
    }
    return len([task for task in graph if task not in blocked_tasks])


def sync_dependency_widget_state(tasks):
    task_names = {task["task"] for task in tasks}
    for task in tasks:
        key = f"deps_{task['task']}"
        valid_choices = task_names - {task["task"]}
        if key in st.session_state:
            task["depends_on"] = [
                dep for dep in st.session_state[key] if dep in valid_choices
            ]


st.set_page_config(page_title="Directed Graph Task Scheduler", layout="wide")
st.title("Directed Graph Task Scheduler")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

with st.sidebar:
    st.header("Task Builder")

    with st.form("task_form", clear_on_submit=True):
        task_name = st.text_input("Task name", placeholder="Example: Compile report")
        existing_tasks = [task["task"] for task in st.session_state.tasks]
        depends_on = st.multiselect("Depends on", existing_tasks)
        submitted = st.form_submit_button("Add task", width="stretch")

    if submitted:
        normalized_name = normalize_task_name(task_name)
        if not normalized_name:
            st.warning("Enter a task name.")
        elif normalized_name in existing_tasks:
            st.warning("Task already exists.")
        else:
            st.session_state.tasks.append(
                {"task": normalized_name, "depends_on": depends_on}
            )
            st.success(f"Added {normalized_name}.")

    st.divider()

    col_a, col_b = st.columns(2)
    if col_a.button("Load sample", width="stretch"):
        st.session_state.tasks = [
            {"task": task["task"], "depends_on": task["depends_on"].copy()}
            for task in SAMPLE_TASKS
        ]
        st.rerun()
    if col_b.button("Clear all", width="stretch"):
        st.session_state.tasks = []
        st.rerun()

tasks = st.session_state.tasks
sync_dependency_widget_state(tasks)

try:
    graph = build_graph(tasks)
    graph_error = None
except ValueError as error:
    graph = {}
    graph_error = str(error)

total_edges = sum(len(neighbours) for neighbours in graph.values())

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Tasks", len(tasks))
metric_b.metric("Dependencies", total_edges)
metric_c.metric("Ready now", count_ready_tasks(graph))

editor_tab, schedule_tab, matrix_tab, graph_tab, analysis_tab = st.tabs(
    ["Tasks", "Schedule", "Adjacency Matrix", "Graph", "Analysis"]
)

with editor_tab:
    st.subheader("Task List")

    if not tasks:
        st.info("Add tasks from the sidebar or load the sample workflow.")
    else:
        for index, task in enumerate(tasks):
            with st.container(border=True):
                col_name, col_deps, col_delete = st.columns([2, 3, 1])
                col_name.markdown(f"**{task['task']}**")

                choices = [
                    item["task"] for item in tasks if item["task"] != task["task"]
                ]
                current_deps = [
                    dep for dep in task.get("depends_on", []) if dep in choices
                ]
                tasks[index]["depends_on"] = col_deps.multiselect(
                    "Depends on",
                    choices,
                    default=current_deps,
                    key=f"deps_{task['task']}",
                    label_visibility="collapsed",
                )

                if col_delete.button(
                    "Delete",
                    key=f"delete_{task['task']}",
                    width="stretch",
                ):
                    remove_task(task["task"])
                    st.rerun()

tasks = st.session_state.tasks

with schedule_tab:
    st.subheader("Execution Order")

    algorithm = st.radio(
        "Algorithm",
        ["BFS", "DFS"],
        horizontal=True,
        captions=[
            "BFS - scheduling.",
            "DFS - cycle detection and ordering.",
        ],
    )

    if graph_error:
        st.error(graph_error)
    elif not tasks:
        st.info("Add tasks before running the scheduler.")
    else:
        result = run_scheduler(algorithm, tasks, graph)
        cycle = find_cycle(graph) if result is None else None

        if cycle:
            st.error("Cycle detected: " + " -> ".join(cycle))
        else:
            st.success(f"{algorithm} produced a valid execution order.")
            result_df = pd.DataFrame(
                {"Step": range(1, len(result) + 1), "Task": result}
            )
            st.dataframe(result_df, hide_index=True, width="stretch")
            st.download_button(
                "Download order as CSV",
                result_df.to_csv(index=False).encode("utf-8"),
                file_name="task_execution_order.csv",
                mime="text/csv",
            )

with matrix_tab:
    st.subheader("Adjacency Matrix")

    if graph_error:
        st.error(graph_error)
    elif not tasks:
        st.info("Add tasks to generate the matrix.")
    else:
        nodes, matrix = adjacency_matrix(tasks, graph)
        matrix_df = pd.DataFrame(matrix, index=nodes, columns=nodes)
        st.caption("Rows are source tasks. Columns are dependent tasks.")

        if total_edges == 0:
            st.info("No dependencies -> graph has no edges.")

        st.dataframe(matrix_df, width="stretch")

with graph_tab:
    st.subheader("Graph Visualization")

    if graph_error:
        st.error(graph_error)
    else:
        figure = draw_graph(tasks, graph)
        st.pyplot(figure, width=720, clear_figure=True)
        plt.close(figure)

with analysis_tab:
    st.subheader("Design Analysis")
    st.dataframe(
        pd.DataFrame(ALGORITHM_DESIGN),
        hide_index=True,
        width="stretch",
    )

    st.subheader("Algorithm Test Cases")
    iterations = st.slider(
        "Timing iterations per test case",
        min_value=100,
        max_value=5000,
        value=500,
        step=100,
    )

    analysis_df = pd.DataFrame(run_analysis(iterations))
    st.dataframe(analysis_df, hide_index=True, width="stretch")
    st.download_button(
        "Download analysis as CSV",
        analysis_df.to_csv(index=False).encode("utf-8"),
        file_name="algorithm_analysis.csv",
        mime="text/csv",
    )

    st.subheader("Test Case Graph Visualization")
    selected_case_name = st.selectbox(
        "Choose test case graph",
        [case["name"] for case in TEST_CASES],
    )
    selected_case = next(
        case for case in TEST_CASES if case["name"] == selected_case_name
    )
    selected_tasks = selected_case["tasks"]
    selected_graph = build_graph(selected_tasks)
    selected_edges = sum(len(neighbours) for neighbours in selected_graph.values())

    graph_info_a, graph_info_b, graph_info_c = st.columns(3)
    graph_info_a.metric("Case tasks", len(selected_tasks))
    graph_info_b.metric("Case edges", selected_edges)
    graph_info_c.metric("Expected", selected_case["expected"])

    if selected_case["expected"] == "Cycle detected":
        cycle = find_cycle(selected_graph)
        if cycle:
            st.error("Cycle path: " + " -> ".join(cycle))

    case_figure = draw_graph(
        selected_tasks,
        selected_graph,
        title=f"{selected_case_name} Graph",
    )
    st.pyplot(case_figure, width=720, clear_figure=True)
    plt.close(case_figure)
