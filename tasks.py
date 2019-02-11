from celery import Celery
from config import Config
import traceback
import pickle
import time
from sys import stdout

config = Config()

app = Celery('tasks', broker=config.REDIS_URL)
app.conf.timezone = 'Europe/Paris'

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(600,
        monitor.s()
    )


@app.task
def monitor():
    list_ = extract_table(config.MONITOR_URL, classes='listing-list')
    process_list(list_)