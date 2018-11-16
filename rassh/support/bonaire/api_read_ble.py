import psycopg2
import traceback
import requests
import re
import time

from rassh.config.postgres_config import PostgresConfig
from rassh.config.config import Config

config_instance = Config()
config = config_instance.data
postgres_config_instance = PostgresConfig()
postgres_config = postgres_config_instance.data

try:
    with psycopg2.connect(dbname=postgres_config['postgres_dbname'], user=postgres_config['postgres_user'],
                          password=postgres_config['postgres_password'], host=postgres_config['postgres_host']) as conn:
        with conn.cursor() as cur:
            sql = """SELECT ap_wiredmac FROM aps WHERE cancelled_date IS NULL AND zone_id IS NOT NULL"""
            cur.execute(sql)
            aps_rows = cur.fetchall()
            url_base = "http://" + config['api_host'] + ":" + str(config['api_port']) + "/ap/"
            for row in aps_rows:
                try:
                    response = requests.get(url_base + row[0] + "/ble")
                except (requests.Timeout, requests.HTTPError):
                    response = ""
                bles = re.findall(r'"(.*?)"', str(response.content))
                try:
                    ble = bles[0]
                except IndexError:
                    ble = None

                if ble and ble != "message":
                    sql2 = """DELETE FROM controller_ap_bles WHERE ap_wiredmac = %s"""
                    cur.execute(sql2, (row[0],))
                    sql3 = """INSERT INTO controller_ap_bles (ap_wiredmac, ble, last_read)
                                VALUES (%s, %s, NOW())"""
                    cur.execute(sql3, (row[0], ble))

                # Be (very slightly) polite
                time.sleep(0.2)

except psycopg2.DatabaseError:
    print(traceback.format_exc())
    exit("Could not run AP select SQL")
