from collections import defaultdict

def build_graph(tasks):
    graph = defaultdict(list)

    task_names = {t["task"] for t in tasks}

    
    for name in task_names:
        graph[name] = []

    
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