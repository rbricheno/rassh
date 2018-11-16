import psycopg2
import traceback
import requests
import json

from rassh.config.postgres_config import PostgresConfig
from rassh.config.config import Config

config_instance = Config()
config = config_instance.data
postgres_config_instance = PostgresConfig()
postgres_config = postgres_config_instance.data

url = "http://" + config['api_host'] + ":" + str(config['api_port']) + "/ap/"

sql1 = """DELETE FROM controller_aps WHERE ap_wiredmac = %s"""
sql2 = """INSERT INTO controller_aps (ap_wiredmac, ap_group, ap_ip, ap_switch_ip, ap_status, last_read)
              VALUES (%s, %s, %s, %s, %s, NOW())"""

try:
    response = requests.get(url)
except (requests.Timeout, requests.HTTPError):
    response = ""

if response.status_code == 200:
    try:
        with psycopg2.connect(dbname=postgres_config['postgres_dbname'],
                              user=postgres_config['postgres_user'],
                              password=postgres_config['postgres_password'],
                              host=postgres_config['postgres_host']) as conn:
            with conn.cursor() as cur:
                for ap_dict in json.loads(response.content.decode("utf-8")):
                    cur.execute(sql1, (ap_dict['ap_name'],))
                    cur.execute(sql2,
                                (ap_dict['ap_name'],
                                 ap_dict['ap_group'],
                                 ap_dict['ap_ip'],
                                 ap_dict['ap_switch_ip'],
                                 ap_dict['ap_status']))

    except psycopg2.DatabaseError:
        print(traceback.format_exc())
        exit("Could not run AP update SQL")
