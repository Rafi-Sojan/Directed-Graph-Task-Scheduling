def topo_sort_dfs(tasks, graph):
    temporary = set()
    permanent = set()
    order = []

    def dfs(node):
        if node in temporary:
            return False
        if node in permanent:
            return True

        temporary.add(node)

        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False

        temporary.remove(node)
        permanent.add(node)
        order.append(node)
        return True

    for t in tasks:
        node = t["task"]
        if node not in permanent:
            if not dfs(node):
                return None

    return order[::-1]
