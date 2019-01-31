from graph_project.task import TaskGenerator
from graph_project.redis_client import Redis
import datetime
import os

class TaskProcessor:
    def __init__(self,tasks):
        self._tasks = tasks

    def run(self):
        print(f"{self.__class__.__name__} is running on {os.getpid()}")
        a = datetime.datetime.now()
        while True:
            value = Redis.rpop("process")
            if value:
                task = self._find(value)
                if task:
                    task.run()
                    a = datetime.datetime.now()
            b = datetime.datetime.now()
            elapsed = b-a
            if elapsed > datetime.timedelta(minutes=5):
                raise TimeoutError()



    def _find(self,data):
        data = data if type(data) == int else int(data)
        for v in self._tasks:
            #print(f"Task ---> {v}")
            if v.id == data:
                return v
        return None





if __name__ == "__main__":
    # TODO: implement TaskProcessor
    TaskProcessor(tasks=TaskGenerator.generate_tasks()).run()