import psycopg2
import requests

from rassh.api.send_commands import SendCommands
from rassh.api.postgres_nonblocking_put_request import PostgresNonBlockingPutRequest
from rassh.config.postgres_config import PostgresConfig
from rassh.datatypes.well_formed_command import WellFormedCommand

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresSendCommands(SendCommands):
    """This extends the SendCommands class to add support for logging the commands to a PostgreSQL database.
    The same database may then be updated when we receive feedback via the feedback API.
    """

    def __init__(self, put_request_dict_list=None):
        postgres_config_instance = PostgresConfig()
        self.postgres_config = postgres_config_instance.data
        super().__init__(put_request_dict_list)

    def api_put_command(self, request_dict, blocking):
        cmd = WellFormedCommand(self.grammar, request_dict=request_dict)
        send_url = self.url_base + cmd.url

        if cmd.command_name:
            try:
                if self._send_postgres_put_command(cmd.object_type,
                                                   cmd.key_name,
                                                   cmd.target,
                                                   cmd.request,
                                                   send_url,
                                                   cmd.payload, blocking):
                    return True
            except KeyError:
                logger.warning("Key error: missing config?")
                pass
        logger.warning("Error running put command.")
        return False

    def _send_postgres_put_command(self, table_name, key_name, target, command, url, payload, blocking):
        try:
            con = psycopg2.connect(dbname=self.postgres_config['postgres_dbname'],
                                   user=self.postgres_config['postgres_user'],
                                   password=self.postgres_config['postgres_password'],
                                   host=self.postgres_config['postgres_host'])
            with con:
                with con.cursor() as cur:
                    cur.execute(
                        "SELECT " + key_name + " FROM outstanding_config_" + table_name + "s WHERE " + key_name
                        + " = %s AND command = %s AND sent = FALSE", (target, command))
                    if cur.fetchone() is None:
                        cur.execute("INSERT INTO outstanding_config_" + table_name + "s (" + key_name
                                    + ", command, sent, time_requested) VALUES (%s, %s, FALSE, current_timestamp)",
                                    (target, command))
                    else:
                        logger.warning("Could not run command, because there is already outstnding config for target "
                                       + target)
            with con:
                with con.cursor() as cur:
                    if blocking:
                        try:
                            r = requests.put(url, data=payload)
                            if r.status_code == 204:
                                try:
                                    cur.execute("UPDATE outstanding_config_" + table_name + "s SET sent = TRUE, "
                                                + "time_sent = current_timestamp WHERE "
                                                + key_name + " = %s AND command = %s", (target, command))
                                except psycopg2.Error as e:
                                    logger.warning("Postgres error updating list of outstanding config: " + str(e))
                                    return False
                        except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as e:
                            logger.warning("Request error" + str(e))
                            return False
                        return True
                    else:
                        PostgresNonBlockingPutRequest(table_name, key_name, target, command, url, payload)
                        return True

        except psycopg2.Error as e:
            logger.warning("Postgres error getting connection: " + str(e))
            return False
