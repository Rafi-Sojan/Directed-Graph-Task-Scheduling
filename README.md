# Directed Graph Task Scheduling System

A DAG-based task scheduling system built with Python and Streamlit. It lets you create tasks, define dependencies, reject invalid cyclic graphs, and generate a valid execution order for DAGs.

* Topological Sorting using DFS
* Topological Sorting using BFS
* Graph visualization using NetworkX

---

## Features

### Scheduling Algorithms

* DFS -> Depth-first traversal for topological ordering in DAGs
* BFS -> Kahn's algorithm for standard topological ordering

### User Interface

* Sidebar task builder
* Editable dependency list
* Sample workflow loader
* Adjacency matrix view
* CSV export for the execution order
* Directed graph rendering using NetworkX and Matplotlib
* Design analysis and timing test cases for BFS and DFS
* Graph visualization for each algorithm test case
* Individual timing iterations and step-by-step algorithm traces
* Histogram-based timing analysis for increasing graph sizes
* Reproducible random DAG generation with edge probability and seed controls

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
