import threading
import requests
import psycopg2
from rassh.config.postgres_config import PostgresConfig

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresNonBlockingPutRequest(object):
    """This is just like a NonBlockingPutRequest except this also updates the database, if the request was OK."""

    def __init__(self, table_name, key_name, target, command, url, payload):
        postgres_config_instance = PostgresConfig()
        self.postgres_config = postgres_config_instance.data
        self.table_name = table_name
        self.key_name = key_name
        self.target = target
        self.command = command
        self.url = url
        self.payload = payload
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        try:
            r = requests.put(self.url, data=self.payload)
            if r.status_code == 204:
                try:
                    with psycopg2.connect(dbname=self.postgres_config['postgres_dbname'],
                                          user=self.postgres_config['postgres_user'],
                                          password=self.postgres_config['postgres_password'],
                                          host=self.postgres_config['postgres_host']) as con:
                        with con.cursor() as cur:
                            cur.execute("UPDATE outstanding_config_" + self.table_name + "s SET sent = TRUE, "
                                        + "time_sent = current_timestamp WHERE "
                                        + self.key_name + " = %s AND command = %s", (self.target, self.command))
                except psycopg2.Error as e:
                    logger.warning("Postgres error updating list of outstanding config: " + str(e))
                    pass

        except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
            logger.warning("Non-blocking request error: " + str(e))
            pass
