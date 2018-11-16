from rassh.commands.command_base import CommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand


class Queue(CommandBase):
    def __init__(self, expect_manager):
        CommandBase.__init__(self, expect_manager)
        self.object_type = 'queue'
        self.command_name = 'queue'
        self.payload = ['api', ]
        self.default = True
        self.no_target = True

    def run_get_command(self, cmd: WellFormedCommand):
        queue = self.ssh_manager.queue.get_request_queue()
        list_queue = []
        for row in queue:
            dictionary_row = {'rowid': str(row['rowid']), 'request': str(row['request'])}
            list_queue.append(dictionary_row)
        return list_queue, 200

    def run_put_command(self, cmd: WellFormedCommand):
        return "Not implemented", 501
