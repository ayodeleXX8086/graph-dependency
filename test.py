from graph_project.run_processes.run_task_dispatcher import GraphAnalyzer
from graph_project.task import TaskGenerator

build_dependency = GraphAnalyzer(TaskGenerator.generate_tasks())
graph_dependency = build_dependency.build_dependency()
print(graph_dependency)
lst= build_dependency.topology_sort(graph_dependency)
print(lst)



