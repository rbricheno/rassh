#!/usr/bin/python3
import sys

if sys.version_info[0] < 3:
    raise Exception("Python3 required! Current (wrong) version: '%s'" % sys.version_info)

from rassh.api.bonaire_postgres_http_feedback_api import application
