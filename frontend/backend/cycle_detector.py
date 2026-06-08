def find_cycle(graph):
    temporary = set()
    permanent = set()
    path = []

    def visit(node):
        if node in temporary:
            start = path.index(node)
            return path[start:] + [node]
        if node in permanent:
            return None

        temporary.add(node)
        path.append(node)

        for neighbor in graph[node]:
            cycle = visit(neighbor)
            if cycle:
                return cycle

        path.pop()
        temporary.remove(node)
        permanent.add(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle

    return None
