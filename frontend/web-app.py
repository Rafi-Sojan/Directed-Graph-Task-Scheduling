import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from backend.analysis import (
    ALGORITHM_DESIGN,
    benchmark_iterations,
    benchmark_scaling,
    count_edges,
    make_generated_analysis_dag,
    trace_algorithm,
)
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


def draw_scaling_histograms(scaling_df):
    figure, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)

    axes[0].bar(
        scaling_df["Graph Size"],
        scaling_df["DFS Time (ms)"],
        width=3,
        color="#4f46e5",
    )
    axes[0].set_title("DFS Time by Graph Size")
    axes[0].set_xlabel("Number of vertices")
    axes[0].set_ylabel("Average time (ms)")

    axes[1].bar(
        scaling_df["Graph Size"],
        scaling_df["BFS Time (ms)"],
        width=3,
        color="#14b8a6",
    )
    axes[1].set_title("BFS Time by Graph Size")
    axes[1].set_xlabel("Number of vertices")

    figure.tight_layout()
    return figure


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
        ["DFS", "BFS"],
        horizontal=True,
        captions=[
            "DFS - topological ordering for DAGs.",
            "BFS - indegree-based topological ordering.",
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
            st.error(
                "Invalid graph: cycles are not allowed in a DAG. "
                + "Cycle path: "
                + " -> ".join(cycle)
            )
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
    st.subheader("Current DAG Analysis")

    if graph_error:
        st.error(graph_error)
    elif not tasks:
        st.info("Add tasks in the Task Builder to analyze your own DAG.")
    else:
        current_cycle = find_cycle(graph)
        if current_cycle:
            st.error(
                "Invalid graph: analysis requires a DAG. Cycle path: "
                + " -> ".join(current_cycle)
            )
        else:
            current_bfs_timing = pd.DataFrame(
                benchmark_iterations("BFS", tasks, graph, 10)
            )
            current_dfs_timing = pd.DataFrame(
                benchmark_iterations("DFS", tasks, graph, 10)
            )
            current_summary = pd.DataFrame(
                [
                    {
                        "Algorithm": "DFS",
                        "Tasks": len(tasks),
                        "Edges": total_edges,
                        "Average Time (ms)": round(
                            current_dfs_timing["Time Taken (ms)"].mean(), 6
                        ),
                        "Result": "Valid",
                    },
                    {
                        "Algorithm": "BFS",
                        "Tasks": len(tasks),
                        "Edges": total_edges,
                        "Average Time (ms)": round(
                            current_bfs_timing["Time Taken (ms)"].mean(), 6
                        ),
                        "Result": "Valid",
                    },
                ]
            )

            st.dataframe(current_summary, hide_index=True, width="stretch")

            current_graph_figure = draw_graph(
                tasks,
                graph,
                title="Current Task Builder DAG",
            )
            st.pyplot(current_graph_figure, width=720, clear_figure=True)
            plt.close(current_graph_figure)

            current_trace_algorithm = st.radio(
                "Trace current DAG with",
                ["DFS", "BFS"],
                horizontal=True,
                key="current_dag_trace_algorithm",
            )
            current_trace_df = pd.DataFrame(
                trace_algorithm(current_trace_algorithm, tasks, graph)
            )
            st.dataframe(current_trace_df, hide_index=True, width="stretch")

            st.download_button(
                "Download current DAG analysis as CSV",
                current_summary.to_csv(index=False).encode("utf-8"),
                file_name="current_dag_analysis.csv",
                mime="text/csv",
            )

    st.divider()
    st.subheader("Design Analysis")
    st.dataframe(
        pd.DataFrame(ALGORITHM_DESIGN),
        hide_index=True,
        width="stretch",
    )

    st.subheader("Generated DAG Analysis")
    generated_col_a, generated_col_b = st.columns(2)
    generated_dag_type = generated_col_a.selectbox(
        "Generated DAG type",
        ["Non-Random DAG", "Random DAG"],
    )
    generated_dag_size = generated_col_b.slider(
        "Generated DAG size",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
    )
    generated_edge_probability = 0.15
    generated_seed = 42

    if generated_dag_type == "Random DAG":
        generated_random_col_a, generated_random_col_b = st.columns(2)
        generated_edge_probability = generated_random_col_a.slider(
            "Generated DAG edge probability",
            min_value=0.01,
            max_value=0.50,
            value=0.15,
            step=0.01,
        )
        generated_seed = generated_random_col_b.number_input(
            "Generated DAG random seed",
            min_value=1,
            max_value=9999,
            value=42,
            step=1,
        )
    generated_iterations = st.slider(
        "Timing iterations for generated DAG summary",
        min_value=100,
        max_value=5000,
        value=500,
        step=100,
    )

    selected_tasks = make_generated_analysis_dag(
        generated_dag_size,
        generated_dag_type,
        generated_edge_probability,
        generated_seed,
    )
    selected_graph = build_graph(selected_tasks)
    selected_edges = count_edges(selected_graph)
    generated_dfs_timing = pd.DataFrame(
        benchmark_iterations(
            "DFS",
            selected_tasks,
            selected_graph,
            generated_iterations,
        )
    )
    generated_bfs_timing = pd.DataFrame(
        benchmark_iterations(
            "BFS",
            selected_tasks,
            selected_graph,
            generated_iterations,
        )
    )
    generated_summary = pd.DataFrame(
        [
            {
                "DAG Type": generated_dag_type,
                "Algorithm": "DFS",
                "Vertices": len(selected_tasks),
                "Edges": selected_edges,
                "Average Time (ms)": round(
                    generated_dfs_timing["Time Taken (ms)"].mean(), 6
                ),
                "Result": "Valid",
            },
            {
                "DAG Type": generated_dag_type,
                "Algorithm": "BFS",
                "Vertices": len(selected_tasks),
                "Edges": selected_edges,
                "Average Time (ms)": round(
                    generated_bfs_timing["Time Taken (ms)"].mean(), 6
                ),
                "Result": "Valid",
            },
        ]
    )
    st.dataframe(generated_summary, hide_index=True, width="stretch")
    st.download_button(
        "Download generated DAG analysis as CSV",
        generated_summary.to_csv(index=False).encode("utf-8"),
        file_name="generated_dag_analysis.csv",
        mime="text/csv",
    )

    graph_info_a, graph_info_b, graph_info_c = st.columns(3)
    graph_info_a.metric("Case tasks", len(selected_tasks))
    graph_info_b.metric("Case edges", selected_edges)
    graph_info_c.metric("Expected", "Valid DAG")

    case_figure = draw_graph(
        selected_tasks,
        selected_graph,
        title=f"{generated_dag_type} ({generated_dag_size} vertices)",
    )
    st.pyplot(case_figure, width=720, clear_figure=True)
    plt.close(case_figure)

    st.subheader("Individual Iteration Timing")
    timing_algorithm = st.radio(
        "Algorithm for individual timing",
        ["DFS", "BFS"],
        horizontal=True,
        key="individual_timing_algorithm",
    )
    timing_runs = st.slider(
        "Number of individual timing runs",
        min_value=1,
        max_value=100,
        value=10,
        step=1,
    )
    timing_df = pd.DataFrame(
        benchmark_iterations(
            timing_algorithm,
            selected_tasks,
            selected_graph,
            timing_runs,
        )
    )

    timing_metric_a, timing_metric_b, timing_metric_c = st.columns(3)
    timing_metric_a.metric(
        "Fastest run (ms)",
        f"{timing_df['Time Taken (ms)'].min():.6f}",
    )
    timing_metric_b.metric(
        "Slowest run (ms)",
        f"{timing_df['Time Taken (ms)'].max():.6f}",
    )
    timing_metric_c.metric(
        "Average run (ms)",
        f"{timing_df['Time Taken (ms)'].mean():.6f}",
    )
    st.dataframe(timing_df, hide_index=True, width="stretch")
    st.download_button(
        "Download individual timing as CSV",
        timing_df.to_csv(index=False).encode("utf-8"),
        file_name="individual_iteration_timing.csv",
        mime="text/csv",
    )

    st.subheader("Algorithm Iteration Trace")
    trace_algorithm_name = st.radio(
        "Algorithm for step trace",
        ["DFS", "BFS"],
        horizontal=True,
        key="trace_algorithm",
    )
    trace_df = pd.DataFrame(
        trace_algorithm(trace_algorithm_name, selected_tasks, selected_graph)
    )
    st.dataframe(trace_df, hide_index=True, width="stretch")

    st.subheader("Graph Size Timing Histograms")
    hist_col_a, hist_col_b, hist_col_c = st.columns(3)
    max_graph_size = hist_col_a.slider(
        "Maximum graph size",
        min_value=20,
        max_value=500,
        value=100,
        step=20,
    )
    size_step = hist_col_b.slider(
        "Size interval",
        min_value=10,
        max_value=100,
        value=20,
        step=10,
    )
    scaling_repetitions = hist_col_c.slider(
        "Runs per size",
        min_value=10,
        max_value=1000,
        value=100,
        step=10,
    )
    scaling_graph_type = st.selectbox(
        "Graph type for size experiment",
        ["Linear", "Branching", "Independent", "Random DAG"],
    )
    random_edge_probability = 0.15
    random_seed = 42

    if scaling_graph_type == "Random DAG":
        random_col_a, random_col_b = st.columns(2)
        random_edge_probability = random_col_a.slider(
            "Random edge probability",
            min_value=0.01,
            max_value=0.50,
            value=0.15,
            step=0.01,
        )
        random_seed = random_col_b.number_input(
            "Random seed",
            min_value=1,
            max_value=9999,
            value=42,
            step=1,
        )

    scaling_df = pd.DataFrame(
        benchmark_scaling(
            max_graph_size,
            size_step,
            scaling_graph_type,
            scaling_repetitions,
            random_edge_probability,
            random_seed,
        )
    )
    scaling_figure = draw_scaling_histograms(scaling_df)
    st.pyplot(scaling_figure, width=760, clear_figure=True)
    plt.close(scaling_figure)
    st.dataframe(scaling_df, hide_index=True, width="stretch")
    st.download_button(
        "Download graph-size timing as CSV",
        scaling_df.to_csv(index=False).encode("utf-8"),
        file_name="graph_size_timing.csv",
        mime="text/csv",
    )
