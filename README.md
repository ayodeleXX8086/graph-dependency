# graph-dependency
This program manages tasks in a graph representation and executes the task by topologically sorting task based on their ordering, each dependant task are executed parallelly. This program shows an example of managing large complex task that could be used as an asynchronous mode for task management classic example of task management is Luigi or Airflow.

# Example
We are representing each of the task for now as an Integer, this could be an reference to a trigger.
graph = {5: {1, 2}, 
        6: {1, 2, 3, 4}, 
        7: {1, 2, 3, 4, 5, 6}}
What happens is that it topologically sorts the graph in this manner [1, 2, 3, 4, 5, 6, 7], and also execute the task in this manner also
Task 5 will not execute until Task 1 and Task 2,Task 6 will not get executed until Task 1,2,3,4 are executed and Task 7 will not get executed until Task 1,2,3,4,5,6. Meanwhile Task 1,2,3,4 are indenpendent this tasks will be parallely.

# Running the application
install redis server
pip -r requirements.txt
python main.py
