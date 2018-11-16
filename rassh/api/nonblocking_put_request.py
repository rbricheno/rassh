import threading
import requests


class NonBlockingPutRequest(object):
    """For when you want to fire off a request, and don't care about the response. (This probably never happens.)"""

    def __init__(self, url, payload):
        self.url = url
        self.payload = payload
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        try:
            requests.put(self.url, data=self.payload)
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
            pass
