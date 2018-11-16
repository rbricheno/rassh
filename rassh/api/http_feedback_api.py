"""This lets you run a simple feedback API, without any database support."""

from flask import Flask
from flask_restful import Api

from rassh.config.config import Config
from rassh.api.resources.feedback import Feedback

application = Flask(__name__)
api = Api(application)

api.add_resource(Feedback, '/')

if __name__ == '__main__':
    application.run(port=Config().data['feedback_port'], debug=True, use_reloader=False)
