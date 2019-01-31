from graph_project.redis_client import Redis
from time import sleep


class Task(object):
    def __init__(self, id=None, tasks=None,delay=None):
        """
        :param id: integer which is used to identify the output of the task in redis
        :param tasks: list of Task, this Task depends on or None
        """

        assert isinstance(id, int)

        if tasks is None:
            # no subtasks
            tasks = []

        self.id = id
        self.tasks = tasks # these are the subtasks
        self.delay= delay if delay else 3

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return f"{self.id}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.__class__==other.__class__ and self.id==other.id)

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def run(self):
        """ This performs some calculation using the subtasks (if any), then store the output in Redis.
        """
        print("Running task {0}".format(self.id))

        # Run calculation
        if len(self.tasks) == 0:
            # No subtask, output = id
            value = self.id
        else:
            """ Add up output of the subtasks
            """
            value = 0

            for task in self.tasks:
                task_output = Redis.get_value(task.id)
                assert not task_output is None, "Missing task output for subtask {0}".format(task.id)
                value += int(task_output)
            sleep(3)

        # Save output in redis
        print("Setting value = {0} for task {0}".format(value, self.id))
        Redis.set_value(self.id, value)
        Redis.rpush("done",self.id)

class TaskGenerator(object):

    @classmethod
    def generate_tasks(self):
        """ This returns a list of tasks
        """
        tasks_level_1 = [Task(1), Task(2), Task(3), Task(4)]
        tasks_level_2 = [Task(5, tasks=tasks_level_1[0:2]), Task(6, tasks=tasks_level_1)] # Ask if this a bug
        tasks_level_3 = [Task(7, tasks=tasks_level_1 + tasks_level_2)]

        return tasks_level_1 + tasks_level_2 + tasks_level_3


