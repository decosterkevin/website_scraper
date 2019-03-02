from decouple import config

class Config(object):
    MONITOR_URL = config("MONITOR_URL")
    EMAIL_PASSWORD = config("EMAIL_PASSWORD")
    EMAIL_USERNAME = config("EMAIL_USERNAME")
    EMAIL_PORT = config("EMAIL_PORT")
    EMAIL_HOST = config("EMAIL_HOST")
    REDIS_URL = config("REDIS_URL")
    PERSITANT_STORAGE = config("PERSITANT_STORAGE", default="data/")
    ROOT_URL = config("ROOT_URL", default="https://www.anibis.ch")
    HOST = config("HOST")
    
    BACKUP_JSON_FILE = PERSITANT_STORAGE + 'backup.json'