from collections import defaultdict
import heapq

def schedule(tasks, graph):
    indegree = defaultdict(int)
    priority_map = {}

    
    for t in tasks:
        name = t["task"]
        priority = int(t["priority"].split()[1])   
        priority_map[name] = priority
        indegree[name] = 0

    
    for u in graph:
        for v in graph[u]:
            indegree[v] += 1

    heap = []
    for node in indegree:
        if indegree[node] == 0:
            heapq.heappush(heap, (priority_map[node], node))

    order = []

    while heap:
        pr, node = heapq.heappop(heap)
        order.append(node)

        for nei in graph[node]:
            indegree[nei] -= 1
            if indegree[nei] == 0:
                heapq.heappush(heap, (priority_map[nei], nei))

    if len(order) != len(tasks):
        return None

    return order