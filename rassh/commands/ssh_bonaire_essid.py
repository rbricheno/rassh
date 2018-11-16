from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.commands import bonaire_functions


class SSHBonaireESSID(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ssid_profile'
        self.command_name = 'essid'
        self.payload = ['essid', ]

    def run_get_command(self, cmd: WellFormedCommand):
        lines = self.expect_command(self.ssh_manager.master_controller,
                                 "show wlan ssid-profile " + cmd.request_dict['target']
                                    + " | include ESSID", cmd)

        essid = None
        for line in lines:
            if line.startswith("ESSID"):
                essid = line.replace("ESSID", "", 1).strip()
            if line.startswith("SSID Profile"):
                # """SSID Profile "fake_ssid_profile" undefined."""
                return "Error: SSID profile not found", 404
        if not essid:
            return "Error: could not parse ESSID", 500

        return essid, 200

    def run_put_command(self, cmd: WellFormedCommand):
        length = len(cmd.request_dict['params']['essid'])
        if length < 1 or length > 32:
            return "Error: ESSID must be between 1 and 32 characters (check failed).", 501

        _ = self.expect_command(self.ssh_manager.master_controller, "configure t", cmd)

        _ = self.expect_command(self.ssh_manager.master_controller,
                             "wlan ssid-profile " + cmd.request_dict['target'], cmd)

        lines = self.expect_command(self.ssh_manager.master_controller, 'essid "'
                                    + cmd.request_dict['params']['essid'] + '"', cmd)

        for line in lines:
            if line.startswith("% Invalid input detected at '^' marker."):
                # You see this if attempting to set an ESSID which is too short or long (for example).
                # This should have been handled by the earlier check, so 500 is appropriate.
                bonaire_functions.end_end(self, cmd)
                return "Server Error: ESSID must be between 1 and 32 characters (failed).", 500

        bonaire_functions.end_end(self, cmd)

        _ = self.expect_command(self.ssh_manager.master_controller, "write mem", cmd)

        return cmd.request_dict['params']['essid'], 204
