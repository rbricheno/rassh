import psycopg2

from rassh.config.postgres_config import PostgresConfig

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresFunctions:
    """This is a utility class that contains queries to run against PostgreSQL on the application server."""
    def __init__(self):
        postgres_config_instance = PostgresConfig()
        self.postgres_config = postgres_config_instance.data

    def completed_config(self, table_name, key_name, target, command, response, status, completed):
        try:
            with psycopg2.connect(dbname=self.postgres_config['postgres_dbname'],
                                  user=self.postgres_config['postgres_user'],
                                  password=self.postgres_config['postgres_password'],
                                  host=self.postgres_config['postgres_host']) as con:
                with con.cursor() as cur:
                    cur.execute(
                        "SELECT " + key_name + " FROM latest_" + table_name + "_config_results WHERE " + key_name
                        + " = %s", (target,))
                    if cur.fetchone() is None:
                        cur.execute(
                            "INSERT INTO latest_" + table_name + "_config_results (" + key_name
                            + ", response, status, last_updated) VALUES (%s, %s, %s, current_timestamp)",
                            (target, response, status))
                    else:
                        cur.execute(
                            "UPDATE latest_" + table_name + "_config_results SET response = %s, status = %s WHERE "
                            + key_name + " = %s", (response, status, target))
                    cur.execute(
                        "INSERT INTO logged_config_" + table_name + "s (" + key_name
                        + ", command, response, status, time_completed) VALUES (%s, %s, %s, %s, current_timestamp)",
                        (target, command, response, status))
                    if completed:
                        cur.execute(
                            "DELETE FROM outstanding_config_" + table_name + "s WHERE " + key_name
                            + " = %s AND command = %s", (target, command))
            return True
        except psycopg2.Error as e:
            logger.error("Database error when handling feedback.")
            logger.error(e)
            return False
