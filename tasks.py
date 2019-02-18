from celery import Celery
from config import Config
import traceback
import pickle
import time
from sys import stdout
from collections import defaultdict
from lib import extract_table, process_list, send_mail
import json
import os.path
from bson import json_util

config = Config()
FILE_NAME_PKL= 'backup.pkl'
FILE_PATH = config.PERSITANT_STORAGE + FILE_NAME_PKL
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
    BACKUP_JSON_FILE=config.PERSITANT_STORAGE + 'backup.json'

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
        for id_, conf in data.items():
            print(f'processing url #{id_}')
            base_url = conf.get("url")
            filters = conf.get("filters", None)
            if not filters:
                print(' not filer found, processing base url...')
                list_ = extract_table(base_url, classes='listing-list')
                new_offers.extend(process_list(list_, results.get(id_, None)))
                results[id_] = list_

            else:
                print(f'{len(filters)} filters found, processing...')
                for index, filter_ in enumerate(filters):
                    url = base_url + "&fts={}".format(filter_)
                    list_ = extract_table(url, classes='listing-list')
                    res = results.get(id_, None)
                    if res and len(res) > index: 
                        fil = res[filter_]
                    else:
                        fil = None
                    new_offers.extend(process_list(list_, fil))
                    if not results.get(id_, None):
                        results[id_] = {}
                    results[id_][filter_] = list_
        
        print('all urls processed, ending...')
        if len(new_offers) > 0:
            print(f'{len(new_offers)} founds, sending email...')
            send_mail(new_offers)
        print('dumping latest results...')
        jres = json.dumps(results, default=str)
        with open(BACKUP_JSON_FILE, 'w') as file:
            file.write(jres)
        print('finished.')
