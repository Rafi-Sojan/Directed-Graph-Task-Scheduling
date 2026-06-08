def build_graph(tasks):
    graph = {task["task"]: [] for task in tasks}
    task_names = set(graph)

    for t in tasks:
        task = t["task"]
        for dep in t.get("depends_on", []):
            if dep not in task_names:
                raise ValueError(f"Invalid dependency: {dep}")
            if dep == task:
                raise ValueError(f"Task '{task}' cannot depend on itself")
            if task not in graph[dep]:
                graph[dep].append(task)

    return graph
