import datetime

from graph_project.redis_client import Redis
from graph_project.run_processes.run_task_dispatcher import TaskDispatcher, TaskGenerator
from graph_project.run_processes.run_task_processor import TaskProcessor
from flask import Flask,render_template
from flask_socketio import SocketIO
from time import sleep
from threading import Thread,Event
import multiprocessing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
task_updater = Thread()
stop_event = Event()

class TaskUpdater(Thread):
    def __init__(self):
        self.delay=3
        super(TaskUpdater,self).__init__()
    def updater(self):

        while not stop_event.is_set():
            process = Redis.rpop("done")
            if process:
                value = Redis.get_value(process)
                print("The json payload {} ".format({'process':process,'value':value}))
                socketio.emit('update_event',{'process':process,'value':value},namespace='/update')
                sleep(self.delay)

    def run(self):
        self.updater()


@app.route("/start",methods=['GET'])
def start():
    return "<html><body><h2>The Start Button</h2><form action='/start' method='post'><input type='submit' value='Start processes'></form></body></html>"

@app.route("/start",methods=['POST'])
def start_process():
    print("Started process --------------> ")
    task1 = TaskDispatcher(tasks=TaskGenerator().generate_tasks())
    task2 = TaskProcessor(tasks=TaskGenerator().generate_tasks())
    p1 = multiprocessing.Process(target=task1.run)
    p2 = multiprocessing.Process(target=task2.run)
    p1.start()
    p2.start()
    return render_template('table.html')

@socketio.on('connect',namespace='/update')
def connect_update():
    global task_updater
    print('Websocket connected')
    if not task_updater.isAlive():
        task_updater = TaskUpdater()
        task_updater.start()

@socketio.on('disconnect',namespace='/update')
def disconnect_update():
    print('Websocket disconnected')

if __name__ == '__main__':
    socketio.run(app, use_reloader=False)