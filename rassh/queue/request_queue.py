import sqlite3
import os
import time
import threading
import requests

from rassh.config.config import Config

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RequestQueue:
    """Sometimes, requests may not be processed right away. A command may time out, or the target system may be in
    a state that prevents a command from running immediately. The RequestQueue allows requests to be enqueued for
    later processing. A queue run is performed roughly every two minutes in an attempt to empty the queue by
    re-running the enqueued commands.

    Similarly, it may not be possible for feedback to be posted right away. Outstanding feedback is also enqueued
    for processing on the next queue run in the same way as outstanding requests."""

    config_instance = Config()
    config = config_instance.data

    if os.path.isdir('/var/lib/rassh'):
        logger.info("Using system-wide queue directory /var/lib/rassh")
        dir_path = '/var/lib/rassh'
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/data"
        logger.info("Using module-local queue directory " + dir_path)

    def __init__(self, expect_manager):
        self.manager = expect_manager
        self.worker_thread = threading.Thread(name='queue', target=self.keep_processing_queue_forever)
        self.worker_thread.start()

    def queue_run(self):
        logger.debug("Starting queue run")
        queue = self.get_request_queue()
        for row in queue:
            logger.debug("Handling queue row " + str(row['rowid']))
            self.handle_request(int(row['rowid']), str(row['request']))

    def feedback_queue_run(self):
        logger.debug("Starting feedback queue run")
        queue = self.get_feedback_queue()
        for row in queue:
            logger.debug("Handling feedback row " + str(row['rowid']))
            self.handle_feedback(int(row['rowid']), str(row['request']), str(row['response']), int(row['status']))

    def keep_processing_queue_forever(self):
        while True:
            logger.debug("Starting queue runs")
            self.queue_run()
            self.feedback_queue_run()
            # Don't run the queue more frequently than once every 2 minutes.
            time.sleep(120)

    def get_db_safely(self):
        full_database_path = RequestQueue.dir_path + '/sshqueue'
        try:
            db = sqlite3.connect(full_database_path)
            # The below line is magic which allows us to use names for returned values rather than tuple indices.
            db.row_factory = sqlite3.Row
        except sqlite3.OperationalError:
            logger.error("Could not open database file " + full_database_path)
            logger.error("Please check that the directory exists and is writable by the rassh process.")
            raise
        return db

    def get_request_queue(self):
        try:
            self.create_request_queue_if_not_exists()
            queue = []
            db = self.get_db_safely()
            cursor = db.cursor()
            cursor.execute(
                """SELECT rowid, request FROM queue ORDER BY rowid ASC""")
            for row in cursor:
                queue.append(row)
            return queue
        except sqlite3.Error:
            return []

    def get_feedback_queue(self):
        try:
            self.create_feedback_queue_if_not_exists()
            queue = []
            db = self.get_db_safely()
            cursor = db.cursor()
            cursor.execute(
                """SELECT rowid, request, response, status FROM feedback_queue ORDER BY rowid ASC""")
            for row in cursor:
                queue.append(row)
            return queue
        except sqlite3.Error as e:
            logger.error("Database error when getting feedback queue.")
            logger.error(e)
            return []

    def handle_request(self, rowid: int, request: str):
        # 408 is not considered a fatal error here, we want to try and run the command again when the system may be
        # less busy.
        fatal_errors = [400, 404, 500, 501]

        logger.debug("Trying to run enqueued request: " + request)
        response = self.manager.request(request=request)
        if response.get_code() == 204:
            # Hooray! Command was run ok and can be dequeued.
            self.dequeue_request_by_rowid(rowid)
            logger.debug("Request was successful and has been dequeued: " + request)
        if response.get_code() in fatal_errors:
            # Something went so wrong that it isn't even worth trying this again, dequeue it.
            self.dequeue_request_by_rowid(rowid)
            logger.debug("Request failed permanently and has been dequeued: " + request)

    def handle_feedback(self, feedback_rowid: int, request: str, response: str, status: int):
        feedback_payload = {'request': request, 'response': response, 'status': status}
        feedback_url = 'http://' + self.config['feedback_host'] + ':' + str(self.config['feedback_port']) + '/'
        try:
            r = requests.post(feedback_url, data=feedback_payload)
            logger.debug("Feedback posted to " + feedback_url)
            if r.status_code == 204:
                self.dequeue_feedback_by_rowid(feedback_rowid)
                logger.debug("Feedback dequeued.")
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
            logger.warning("Feedback timed out posting to " + feedback_url)
            pass

    def enqueue_request(self, request: str) -> bool:
        self.create_request_queue_if_not_exists()
        if request is not None:
            if self.request_already_queued(request):
                return True
            else:
                try:
                    db = self.get_db_safely()
                    cursor = db.cursor()
                    cursor.execute(
                        """INSERT INTO queue (request) VALUES (?)""",
                        (str(request),))
                    db.commit()
                    if self.config['feedback']:
                        if self.enqueue_feedback(request, "Command has been enqueued", 202):
                            logger.debug("Feedback sent or enqueued.")
                        else:
                            logger.warning("Error when enqueueing feedback.")
                    return True
                except sqlite3.Error:
                    return False
        return False

    def request_already_queued(self, request: str):
        """Returns False if there is no record of this request in the queue."""
        try:
            self.create_request_queue_if_not_exists()
            queue = []
            db = self.get_db_safely()
            cursor = db.cursor()
            cursor.execute(
                """SELECT rowid FROM queue WHERE request = ?""",
                (request,))
            for row in cursor:
                queue.append(row)
            if len(queue) == 0:
                return False
            else:
                return True
        except sqlite3.Error:
            # This is a lie, but we don't want to try and enqueue something if we got an error here.
            return True

    def create_request_queue_if_not_exists(self):
        db = self.get_db_safely()
        cursor = db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS queue(request TEXT NOT NULL)""")

    def enqueue_feedback(self, request: str, response: str, status: int):
        self.create_feedback_queue_if_not_exists()
        if request is not None:
            try:
                db = self.get_db_safely()
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO feedback_queue (request, response, status) VALUES (?, ?, ?)""",
                    (str(request), str(response), int(status)))
                db.commit()
            except sqlite3.Error as e:
                logger.error("Database error when enqueueing feedback.")
                logger.error(e)
                return False
        else:
            return False
        # Try and send the latest feedback immediately.
        self.feedback_queue_run()
        return True

    def create_feedback_queue_if_not_exists(self):
        db = self.get_db_safely()
        cursor = db.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS
                   feedback_queue(request TEXT NOT NULL, response TEXT, status INTEGER NOT NULL)""")

    def dequeue_request_by_rowid(self, rowid: int):
        try:
            db = self.get_db_safely()
            cursor = db.cursor()
            cursor.execute(
                'DELETE FROM queue WHERE rowid = ?', (rowid,))
            db.commit()
        except sqlite3.Error as e:
            # The queue item may have been deleted while we were in flight, so don't die here...
            logger.warning("Database error when deleting queue item.")
            logger.warning(e)
            pass

    def dequeue_feedback_by_rowid(self, feedback_rowid: int):
        try:
            db = self.get_db_safely()
            cursor = db.cursor()
            cursor.execute(
                'DELETE FROM feedback_queue WHERE rowid = ?', (feedback_rowid,))
            db.commit()
        except sqlite3.Error as e:
            # The queue item may have been deleted while we were in flight, so don't die here...
            logger.warning("Database error when deleting feedback queue item.")
            logger.warning(e)
            pass
