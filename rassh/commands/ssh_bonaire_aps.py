import re
from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand


class SSHBonaireAPs(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'aps'
        self.default = True
        self.no_target = True
        self.payload = []

    def run_get_command(self, cmd: WellFormedCommand):
        http_status = 200
        lines = self.expect_command(self.ssh_manager.master_controller, "show ap database", cmd)

        data = []
        if lines:
            for line in lines:
                ap_name = re.search(r'^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', line, re.I)
                try:
                    ap_name_group = ap_name.group()
                    fields = re.split(r'\s{2,}', line)
                    try:
                        data.append({'ap_name': ap_name_group,
                                     'ap_group': fields[1],
                                     'ap_type': fields[2],
                                     'ap_ip': fields[3],
                                     'ap_status': fields[4],
                                     'ap_flags': fields[5],
                                     'ap_switch_ip': fields[6],
                                     'ap_standby_ip': fields[7]})
                    except IndexError:
                        pass
                except AttributeError:
                    pass
        else:
            http_status = 404

        return data, http_status

    def run_put_command(self, cmd: WellFormedCommand):
        # Not implemented by the host system.
        return "Not implemented.", 501
