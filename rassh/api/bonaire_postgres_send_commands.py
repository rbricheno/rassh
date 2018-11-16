from rassh.api.postgres_send_commands import PostgresSendCommands
from rassh.managers.bonaire_ssh_commands import BonaireSSHCommands


class BonairePostgresSendCommands(PostgresSendCommands):
    """This extends the PostgresSendCommands class to add support for the Bonaire API commands."""

    def _my_grammar(self):
        commands = BonaireSSHCommands(None)
        return commands.grammar
