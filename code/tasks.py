__author__ = 'mariosky'


BROKER_URL = 'redis://localhost:6379/0'

from celery import Celery

app = Celery('tasks', broker=BROKER_URL, backend='redis://localhost')
app.conf.CELERY_TASK_SERIALIZER = 'json'

@app.task
def add(x, y):
    return x + y

@app.task
def substract(x, y):
    return x - y