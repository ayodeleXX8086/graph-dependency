from graph_project.redis_client import Redis
from functools import reduce
import datetime
import os
from graph_project.task import TaskGenerator


class AbstractTaskDispatcherExcepiton(Exception):
    def __init__(self,message):
        super(AbstractTaskDispatcherExcepiton, self).__init__(message)


class CyclicDependencyException(AbstractTaskDispatcherExcepiton):
    def __init__(self,message,data):
        super(CyclicDependencyException, self).__init__(message)
        self.data = data



class ProcessTimeOutException(AbstractTaskDispatcherExcepiton):
    def __init__(self,pid):
        super(ProcessTimeOutException,self).__init__(f"The process {pid} as timed out")
        self.message = f"The process {pid} as timed out"




class TaskDispatcher:
    def __init__(self,tasks):
        self._tasks             = tasks
        self.graph_analyzer     = GraphAnalyzer(tasks)
        self._graph_dependency  =  self.graph_analyzer.build_dependency()
        self._graph_topology    =  self.graph_analyzer.topology_sort(self._graph_dependency)

    def run(self):
        """
        The run method will stream through the topology list and set them in the queue for the process to pick them,
        It will first check to see if the dependencies(from the graph_dependency) are completed on the queue then will send the dependant value to the
        queue
        :return:
        """
        print(f"{self.__class__.__name__} is running on {os.getpid()}")
        topology = self._graph_topology
        for v in topology:
            if self._graph_dependency.get(v,None):
                dependencies = self._graph_dependency.get(v)
                for dep in dependencies:
                    start = datetime.datetime.now()
                    while True:
                        if Redis.get_value(dep.id):
                            break
                        end = datetime.datetime.now()
                        elapsed = end-start
                        if elapsed > datetime.timedelta(seconds=20):
                            raise ProcessTimeOutException(dep.id)
                Redis.rpush(queue_name="process",value=v.id)
            else:
                Redis.rpush(queue_name="process",value=v.id)






class GraphAnalyzer:
    def __init__(self,tasks):
        self.tasks = tasks

    def build_dependency(self):
        '''This will be the dependency of the list to become a map{task:[]}
          example  [Task(3,tasks=[Task(1),Task(2)]),Task(4,tasks=[Task(7),Task(8)]]
            {
                3:[1,2],
                4:[7,8]
            }
        '''
        dependency=dict()
        for task in self.tasks:
            self._dfs(task,dependency)
        dependency = {k:v for k,v in dependency.items() if v}
        return dependency

    def _dfs(self,task,map):
        map[task]=set()#to avoid cyclic dependency
        for v in task.tasks:
            map[task].add(v)
            if map.get(v,None):
                self._dfs(v,map)

    def topology_sort(self,data):
        """
        Dependencies are expressed as a dictionary whose keys are items
        and whose values are a set of dependent items. Output is a flattened list in topological order.
        :reference: https://pypi.org/project/toposort/
        """
        if len(data) == 0:
            return

        # Copy the input so as to leave it unmodified.
        data = data.copy()

        # Ignore self dependencies.
        for k, v in data.items():
            v.discard(k)
        # Find all items that don't depend on anything.
        extra_items_in_deps = reduce(set.union, data.values()) - set(data.keys())
        # Add empty dependences where needed.
        data.update({item: set() for item in extra_items_in_deps})
        result=[]
        while True:
            ordered = set(item for item, dep in data.items() if len(dep) == 0)
            if not ordered:
                break
            result.extend(list(ordered))
            data = {item: (dep - ordered)
                    for item, dep in data.items()
                    if item not in ordered}
        if len(data)!=0:
            raise CyclicDependencyException("There was a cyclic dependency when sorting the graph ",data)
        return result



if __name__ == "__main__":
    # TODO: implement TaskDispatcher
    Redis.flush_db()
    TaskDispatcher(tasks=TaskGenerator.generate_tasks()).run()