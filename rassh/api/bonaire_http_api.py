"""This lets you run the Bonaire API on the SSH gateway server. It sets up a flask_restful API using the dynamic
resources from the BonaireSSHManager."""

from flask import Flask
from flask_restful import Api

from rassh.managers.bonaire_ssh_manager import BonaireSSHManager
from rassh.api.dynamic_resources import add_dynamic_resources

application = Flask(__name__)
api = Api(application)

add_dynamic_resources(api, BonaireSSHManager.get_instance())

if __name__ == '__main__':
    # It is essential to *not* use the reloader here,
    # or we will exhaust SSH connections very fast!
    application.run(port=BonaireSSHManager.config.get('api_port'), debug=True, use_reloader=False)
