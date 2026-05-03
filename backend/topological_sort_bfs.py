from collections import defaultdict, deque

def topo_sort_dfs(tasks, graph):
    indegree = defaultdict(int)

    for t in tasks:
        indegree[t["task"]] = 0
    
    for u in graph:
        for v in graph[u]:
            indegree[v] += 1
    
    q = deque([node for node in indegree if indegree[node] == 0])
    order = []

    while q:
        node = q.popleft()
        order.append(node)

        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                q.append(neighbour)

        if len(order) != len(tasks):
            return None
        
        return order

