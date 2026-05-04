# Directed Graph Task Scheduling System

A DAG-based task scheduling system built with Python and Streamlit that supports:

* Topological Sorting using BFS
* Topological Sorting using DFS
* Priority-based Scheduling using a Min-Heap
* Graph Visualization using NetworkX

---

## Features

### Multiple Scheduling Algorithms

* BFS → Standard topological ordering
* DFS → Recursive traversal-based ordering
* Priority Scheduling → Chooses highest-priority task among valid options

### Graph Visualization

* Directed graph rendering using NetworkX and Matplotlib
* Color-coded nodes based on priority:

  * Level 1 (High)
  * Level 2 (Medium)
  * Level 3 (Low)

---

## Project Structure

```id="u7s9v1"
frontend/
│
├── web_app.py
│
└── backend/
    ├── __init__.py
    ├── graph_builder.py
    ├── topo_bfs.py
    ├── topo_dfs.py
    ├── priority_scheduler.py
    └── visualizer.py
```

---

## Installation

### 1. Clone the repository

```id="5q4t0x"
git clone https://github.com/your-username/dag-task-scheduler.git
cd dag-task-scheduler/frontend
```

### 2. Install dependencies

```id="d2l9pz"
pip install streamlit networkx matplotlib
```

---

## Run the Application

```id="k8f1bx"
streamlit run web_app.py
```
