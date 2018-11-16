from rassh.api.resources.postgres_feedback import PostgresFeedback
from rassh.managers.bonaire_ssh_commands import BonaireSSHCommands


class BonairePostgresFeedback(PostgresFeedback):
    """This resource is the endpoint for posting all feedback from the Bonaire API. It is populated using the
    lightweight command definitions from BonaireSSHCommands."""
    commands = BonaireSSHCommands(None)
