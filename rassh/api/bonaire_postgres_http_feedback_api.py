"""This lets you run a full-featured feedback API, with PostgreSQL database support for feedback from the Bonaire API.
"""

from flask import Flask
from flask_restful import Api

from rassh.config.config import Config
from rassh.api.resources.bonaire_postgres_feedback import BonairePostgresFeedback

application = Flask(__name__)
api = Api(application)

api.add_resource(BonairePostgresFeedback, '/')

if __name__ == '__main__':
    application.run(port=Config().data['feedback_port'], debug=True, use_reloader=False)
