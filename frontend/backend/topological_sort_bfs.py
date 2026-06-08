from collections import deque


def topo_sort_bfs(tasks, graph):
    indegree = {task["task"]: 0 for task in tasks}

    for u in graph:
        for v in graph[u]:
            indegree[v] += 1

    queue = deque([node for node in indegree if indegree[node] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)

        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)

    if len(order) != len(tasks):
        return None

    return order
