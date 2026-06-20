import random
from time import perf_counter

from backend.graph_builder import build_graph
from backend.topological_sort_bfs import topo_sort_bfs
from backend.topological_sort_dfs import topo_sort_dfs


ALGORITHM_DESIGN = [
    {
        "Algorithm": "DFS",
        "Technique": "Recursive depth-first traversal",
        "Time Complexity": "O(V + E)",
        "Space Complexity": "O(V)",
        "Best Use": "Topological ordering for DAGs",
        "Risk": "Very deep graphs can hit Python recursion limits",
    },
    {
        "Algorithm": "BFS",
        "Technique": "Kahn's algorithm with indegree queue",
        "Time Complexity": "O(V + E)",
        "Space Complexity": "O(V)",
        "Best Use": "Topological ordering using ready-task indegrees",
        "Risk": "Requires maintaining indegree counts",
    },
]


def _make_tasks(names, dependencies):
    return [
        {"task": name, "depends_on": dependencies.get(name, [])}
        for name in names
    ]


def _linear_case(size):
    names = [f"T{i}" for i in range(1, size + 1)]
    dependencies = {
        names[index]: [names[index - 1]]
        for index in range(1, len(names))
    }
    return _make_tasks(names, dependencies)


def _independent_case(size):
    names = [f"T{i}" for i in range(1, size + 1)]
    return _make_tasks(names, {})


def _diamond_case(levels):
    tasks = [{"task": "Start", "depends_on": []}]
    previous_layer = ["Start"]

    for level in range(1, levels + 1):
        current_layer = [f"L{level}A", f"L{level}B"]
        for name in current_layer:
            tasks.append({"task": name, "depends_on": previous_layer.copy()})
        previous_layer = current_layer

    tasks.append({"task": "Finish", "depends_on": previous_layer.copy()})
    return tasks


def make_scaling_case(size, graph_type, edge_probability=0.15, seed=42):
    if graph_type == "Independent":
        return _independent_case(size)
    if graph_type == "Branching":
        return _scaling_branching_case(size)
    if graph_type == "Random DAG":
        return _random_dag_case(size, edge_probability, seed)
    return _linear_case(size)


def _scaling_branching_case(size):
    names = [f"T{i}" for i in range(1, size + 1)]
    dependencies = {}

    for index, name in enumerate(names):
        deps = []
        if index - 1 >= 0:
            deps.append(names[index - 1])
        if index - 2 >= 0 and index % 2 == 0:
            deps.append(names[index - 2])
        dependencies[name] = deps

    return _make_tasks(names, dependencies)


def _random_dag_case(size, edge_probability, seed):
    rng = random.Random(seed + size)
    names = [f"T{i}" for i in range(1, size + 1)]
    dependencies = {name: [] for name in names}

    for source_index, source in enumerate(names):
        for target in names[source_index + 1:]:
            if rng.random() <= edge_probability:
                dependencies[target].append(source)

    return _make_tasks(names, dependencies)


def count_edges(graph):
    return sum(len(neighbours) for neighbours in graph.values())


def benchmark_algorithm(algorithm, tasks, graph, iterations):
    start = perf_counter()
    result = None

    for _ in range(iterations):
        result = algorithm(tasks, graph)

    elapsed = perf_counter() - start
    return result, (elapsed / iterations) * 1000


def benchmark_iterations(algorithm_name, tasks, graph, iterations):
    algorithm = topo_sort_bfs if algorithm_name == "BFS" else topo_sort_dfs
    rows = []

    for iteration in range(1, iterations + 1):
        start = perf_counter()
        result = algorithm(tasks, graph)
        elapsed_ms = (perf_counter() - start) * 1000

        rows.append(
            {
                "Iteration": iteration,
                "Algorithm": algorithm_name,
                "Time Taken (ms)": round(elapsed_ms, 6),
                "Result": "Invalid DAG" if result is None else "Valid",
            }
        )

    return rows


def make_generated_analysis_dag(size, dag_type, edge_probability=0.15, seed=42):
    if dag_type == "Random DAG":
        return _random_dag_case(size, edge_probability, seed)
    return _scaling_branching_case(size)


def benchmark_scaling(
    max_size,
    step_size,
    graph_type,
    repetitions,
    edge_probability=0.15,
    seed=42,
):
    rows = []

    for size in range(step_size, max_size + 1, step_size):
        tasks = make_scaling_case(size, graph_type, edge_probability, seed)
        graph = build_graph(tasks)
        bfs_result, bfs_ms = benchmark_algorithm(
            topo_sort_bfs, tasks, graph, repetitions
        )
        dfs_result, dfs_ms = benchmark_algorithm(
            topo_sort_dfs, tasks, graph, repetitions
        )

        rows.append(
            {
                "Graph Size": size,
                "Graph Type": graph_type,
                "Edges": count_edges(graph),
                "DFS Time (ms)": round(dfs_ms, 6),
                "BFS Time (ms)": round(bfs_ms, 6),
                "DFS Result": "Invalid DAG" if dfs_result is None else "Valid",
                "BFS Result": "Invalid DAG" if bfs_result is None else "Valid",
            }
        )

    return rows


def trace_bfs(tasks, graph):
    indegree = {task["task"]: 0 for task in tasks}

    for source in graph:
        for target in graph[source]:
            indegree[target] += 1

    queue = [node for node in indegree if indegree[node] == 0]
    order = []
    rows = []
    iteration = 1

    while queue:
        queue_before = queue.copy()
        node = queue.pop(0)
        order.append(node)
        unlocked = []

        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)
                unlocked.append(neighbour)

        rows.append(
            {
                "Iteration": iteration,
                "Ready Queue Before": ", ".join(queue_before),
                "Selected Task": node,
                "Unlocked Tasks": ", ".join(unlocked) or "-",
                "Partial Order": " -> ".join(order),
            }
        )
        iteration += 1

    if len(order) != len(tasks):
        rows.append(
            {
                "Iteration": iteration,
                "Ready Queue Before": "-",
                "Selected Task": "Invalid DAG",
                "Unlocked Tasks": "-",
                "Partial Order": "No valid topological order",
            }
        )

    return rows


def trace_dfs(tasks, graph):
    temporary = set()
    permanent = set()
    order = []
    rows = []
    step = 1

    def add_row(action, node, stack):
        nonlocal step
        rows.append(
            {
                "Iteration": step,
                "Action": action,
                "Task": node,
                "Recursion Stack": " -> ".join(stack) or "-",
                "Partial Order": " -> ".join(reversed(order)) or "-",
            }
        )
        step += 1

    def dfs(node, stack):
        if node in temporary:
            add_row("Invalid DAG", node, stack + [node])
            return False
        if node in permanent:
            add_row("Already completed", node, stack)
            return True

        temporary.add(node)
        stack.append(node)
        add_row("Visit", node, stack)

        for neighbor in graph[node]:
            add_row("Explore edge", f"{node} -> {neighbor}", stack)
            if not dfs(neighbor, stack):
                return False

        temporary.remove(node)
        permanent.add(node)
        stack.pop()
        order.append(node)
        add_row("Finish", node, stack)
        return True

    for task in tasks:
        node = task["task"]
        if node not in permanent:
            if not dfs(node, []):
                break

    return rows


def trace_algorithm(algorithm_name, tasks, graph):
    if algorithm_name == "BFS":
        return trace_bfs(tasks, graph)
    return trace_dfs(tasks, graph)


def run_analysis(iterations=500):
    rows = []

    generated_cases = [
        {
            "name": "Non-Random DAG",
            "description": "Deterministic branching DAG generated from selected size.",
            "tasks": make_generated_analysis_dag(20, "Non-Random DAG"),
        },
        {
            "name": "Random DAG",
            "description": "Reproducible random DAG generated from edge probability and seed.",
            "tasks": make_generated_analysis_dag(20, "Random DAG"),
        },
    ]

    for case in generated_cases:
        tasks = case["tasks"]
        graph = build_graph(tasks)
        bfs_result, bfs_ms = benchmark_algorithm(
            topo_sort_bfs, tasks, graph, iterations
        )
        dfs_result, dfs_ms = benchmark_algorithm(
            topo_sort_dfs, tasks, graph, iterations
        )

        rows.append(
            {
                "Test Case": case["name"],
                "Design": case["description"],
                "Tasks": len(tasks),
                "Edges": count_edges(graph),
                "Expected": "Valid DAG order",
                "BFS Result": "Invalid DAG" if bfs_result is None else "Valid",
                "DFS Result": "Invalid DAG" if dfs_result is None else "Valid",
                "BFS Avg Time (ms)": round(bfs_ms, 5),
                "DFS Avg Time (ms)": round(dfs_ms, 5),
                "Faster": "BFS" if bfs_ms <= dfs_ms else "DFS",
            }
        )

    return rows
