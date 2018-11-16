import psycopg2
import traceback
import requests
import re

from rassh.config.postgres_config import PostgresConfig
from rassh.config.config import Config

config_instance = Config()
config = config_instance.data
postgres_config_instance = PostgresConfig()
postgres_config = postgres_config_instance.data

url = "http://" + config['api_host'] + ":" + str(config['api_port']) + "/ap/"

status = ""

try:
    response = requests.get(url)
    groups = re.findall(r"'(.*)\\n'", str(response.content))
    try:
        status = groups[0]
    except IndexError:
        status = None
    if response.status_code == 500:
        status = "Internal server error"
except requests.Timeout:
    status = "Timeout"
except requests.HTTPError:
    status = "HTTP Error"


try:
    with psycopg2.connect(dbname=postgres_config['postgres_dbname'], user=postgres_config['postgres_user'],
                          password=postgres_config['postgres_password'], host=postgres_config['postgres_host']) as conn:
        with conn.cursor() as cur:
            sql = "UPDATE ssh_api_status SET status=%s, time_checked=NOW()"
            cur.execute(sql, (status,))
except psycopg2.DatabaseError:
    print(traceback.format_exc())
    exit("Could not run API status monitor update SQL")
