from time import perf_counter

from backend.graph_builder import build_graph
from backend.topological_sort_bfs import topo_sort_bfs
from backend.topological_sort_dfs import topo_sort_dfs


ALGORITHM_DESIGN = [
    {
        "Algorithm": "BFS",
        "Technique": "Kahn's algorithm with indegree queue",
        "Time Complexity": "O(V + E)",
        "Space Complexity": "O(V)",
        "Best Use": "Task scheduling because ready tasks are explicit",
        "Risk": "None for large DAGs because it is iterative",
    },
    {
        "Algorithm": "DFS",
        "Technique": "Recursive depth-first traversal",
        "Time Complexity": "O(V + E)",
        "Space Complexity": "O(V)",
        "Best Use": "Dependency traversal and cycle checking",
        "Risk": "Very deep graphs can hit Python recursion limits",
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


def _cycle_case():
    return [
        {"task": "A", "depends_on": ["C"]},
        {"task": "B", "depends_on": ["A"]},
        {"task": "C", "depends_on": ["B"]},
    ]


TEST_CASES = [
    {
        "name": "Linear Chain",
        "description": "Every task depends on the previous task.",
        "tasks": _linear_case(12),
        "expected": "Valid order",
    },
    {
        "name": "Independent Tasks",
        "description": "No task depends on another task.",
        "tasks": _independent_case(12),
        "expected": "Any input-order execution is valid",
    },
    {
        "name": "Branching DAG",
        "description": "One workflow splits into parallel branches and merges again.",
        "tasks": _diamond_case(4),
        "expected": "Valid order",
    },
    {
        "name": "Cycle Detection",
        "description": "A depends on C, C depends on B, and B depends on A.",
        "tasks": _cycle_case(),
        "expected": "Cycle detected",
    },
]


def count_edges(graph):
    return sum(len(neighbours) for neighbours in graph.values())


def benchmark_algorithm(algorithm, tasks, graph, iterations):
    start = perf_counter()
    result = None

    for _ in range(iterations):
        result = algorithm(tasks, graph)

    elapsed = perf_counter() - start
    return result, (elapsed / iterations) * 1000


def run_analysis(iterations=500):
    rows = []

    for case in TEST_CASES:
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
                "Expected": case["expected"],
                "BFS Result": "Cycle" if bfs_result is None else "Valid",
                "DFS Result": "Cycle" if dfs_result is None else "Valid",
                "BFS Avg Time (ms)": round(bfs_ms, 5),
                "DFS Avg Time (ms)": round(dfs_ms, 5),
                "Faster": "BFS" if bfs_ms <= dfs_ms else "DFS",
            }
        )

    return rows
