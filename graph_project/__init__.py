"""
CODING INTERVIEW PROBLEM:

==========================================================
FIRST STEP: IMPLEMENT TASK DISPATCHER AND TASK PROCESSOR
==========================================================

-   A task performs some calculations, using possibly the output of other tasks
                    A
                  /  \
                 B   C
                / \ / \
               D   E   F

    For instance, in the graph above, D, E F are the lowest level tasks (they don't depend on any tasks).
    Task B depends on tasks D and E (i.e. tasks D and E needs to have run before task B can be run)
    Task C depends on tasks E and F
    Task A depends on tasks B and C

    -> So in order to calculate task A, we first need to calculate tasks D, E and F, then tasks B and C, before calculating task A.

-   A simple implementation of task is proposed in task.py. The actual task calculation is trivial here, but we could imagine more complex calculations
    (the actual calculation performs by tasks is irrelevant here)

-   TaskGenerator.generate_tasks() return a list of tasks, which defines implicitly a graph of tasks (and again the actual list of tasks is simple here, but we could imagine
    cases with thousands of tasks).

-   The goal is to distribute the calculation of tasks over many processes using the following set up:
    -   One or several task processors runs, each of them executing tasks sequentially
    -   The task dispatcher coordinates the work of the task processors, all the processes communicate via Redis queues:
        - the task dispatcher is aware of the dependencies between the tasks.
        - it first schedule the calculation of the lowest level tasks (which can be run straightaway as they don't depend on anything), then as tasks
        gets done, it schedules more of them. For instance in the example above,
            - when tasks D and E are finished (and not before), then task dispatcher should schedule task B
        - the task dispatcher and task processors should communicate via redis queues. The module redis_client.py defines method rpush, rpop, brpop which should be enough
        for the task dispatcher and task processor to communicate

    - Concretely, if we call:
            python run_task_dispatcher.py

        ...and then call, one or multiple times:
            python run_task_processor.py

        ...then the task should be run till all of them are finished. For your own testing, you may want to try cases where the list of tasks is much larger or where the tasks takes more time
        to run (if there are many tasks or tasks slow to run, then running multiple task processors will speed up the calculation)

        Note that run_task_dispatcher.py calls Redis.flush_db() to clear redis at the beginning of the run.

    - So practically, you need to implement TaskProcessor and TaskDispatcher class


=============================================
SECOND STEP: FLASK GUI WITH MULTIPROCESSING
=============================================

- The second step is to build a little flask server running the task processors and task dispatcher defined in step 1.
    -   The gui consists of:
         -  a button ('start button')
         -  a table with 2 columns: task id and task output. The list of task id is from the id of the tasks (TaskGenerator.generate_tasks()). The task output
            is the output of the task saved in redis (Redis.get_value(task.id)) which is available once the task has run.

    -   At the beginning, there shouldn't be any task output (task not run yet), so the task output column should be empty.

    -   When clicking on start button, the process running flask server should start other python processes:
        -   a task dispatcher
        -   one or several task processors

    -   The flask python process will then keep checking redis for the output of the tasks and populate the table as the tasks gets executed (so if half of the tasks
    have been run so far, then we should see half of the output in the columns).

    - You may want to use a larger number of tasks or slow the tasks so that we can see the table getting populated progressively
"""