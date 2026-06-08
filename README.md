# Directed Graph Task Scheduling System

A DAG-based task scheduling system built with Python and Streamlit. It lets you create tasks, define dependencies, detect cycles, and generate a valid execution order.

* Topological Sorting using BFS
* Topological Sorting using DFS
* Graph visualization using NetworkX

---

## Features

### Scheduling Algorithms

* BFS -> Kahn's algorithm for standard topological ordering
* DFS -> Depth-first traversal with cycle detection

### User Interface

* Sidebar task builder
* Editable dependency list
* Sample workflow loader
* Adjacency matrix view
* CSV export for the execution order
* Directed graph rendering using NetworkX and Matplotlib
* Design analysis and timing test cases for BFS and DFS
* Graph visualization for each algorithm test case

---

## Project Structure

```text
frontend/
|
|-- web-app.py
|
`-- backend/
    |-- __init__.py
    |-- analysis.py
    |-- graph_builder.py
    |-- cycle_detector.py
    |-- topological_sort_bfs.py
    |-- topological_sort_dfs.py
    `-- visualizer.py
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/dag-task-scheduler.git
cd dag-task-scheduler/frontend
```

### 2. Install dependencies

```bash
pip install -r ../requirements.txt
```

---

## Run the Application

```bash
streamlit run web-app.py
```
