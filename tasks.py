from celery import Celery
from config import Config
import traceback
import pickle
import time
from sys import stdout
from collections import defaultdict
from lib import extract_table, process_list, create_email
import json
import os.path
from bson import json_util

config = Config()
app = Celery('tasks', broker=config.REDIS_URL)
app.conf.timezone = 'Europe/Paris'

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Executes every 600 seconds.
    sender.add_periodic_task(600,
        monitor.s()
    )


@app.task
def monitor():
    

    print('loading latest results...')
    if os.path.isfile(BACKUP_JSON_FILE):
        print('... results found in json file. done')
        results = json.load(open(BACKUP_JSON_FILE, 'rb'))
    else:
        print('... results not found, defaulting dictionary')
        results =defaultdict()
    
    new_offers = []
    with open(config.PERSITANT_STORAGE+ 'config.json') as json_file:
        data = json.load(json_file)
        list_to_process = []
        for id_, conf in data.items():
            print(f'processing url #{id_}')
            base_url = conf.get("url")
            filters = conf.get("filters", None)
            extracted_list = []
            if not filters:
                print(' not filer found, processing base url...')
                list_to_process.extend(extract_table(base_url, classes='listing-list'))
            else:
                print(f'{len(filters)} filters found, processing...')
                for index, filter_ in enumerate(filters):
                    url = base_url + "&fts={}".format(filter_)
                    list_to_process.extend(extract_table(url, classes='listing-list'))

        new_offers = process_list(list_to_process, results)
        
        print('all urls processed, ending...')
        if len(new_offers) > 0:
            print(f'{len(new_offers)} founds, sending email...')
            create_email(new_offers)
        
        print('finished.')

