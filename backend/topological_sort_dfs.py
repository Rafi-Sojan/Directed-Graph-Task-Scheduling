def topo_sort_dfs(tasks, graph):
    visited = set()
    rec_stack = set()
    order = []

    def dfs(node):
        if node in rec_stack:
            return False  
        if node in visited:
            return True

        rec_stack.add(node)
        visited.add(node)

        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False

        rec_stack.remove(node)
        order.append(node)
        return True

    for t in tasks:
        node = t["task"]
        if node not in visited:
            if not dfs(node):
                return None  

    return order[::-1]