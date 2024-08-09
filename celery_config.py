from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.update(
    task_annotations={'*': {'rate_limit': '10/s'}}
)
