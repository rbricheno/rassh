from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.datatypes.well_formed_command import WellFormedCommand
from rassh.commands import bonaire_functions


class SSHBonairePSK(SSHBonaireCommandBase):
    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ssid_profile'
        self.command_name = 'psk'
        self.payload = ['psk', ]

    def run_get_command(self, cmd: WellFormedCommand):
        _ = self.expect_command(self.ssh_manager.master_controller, "encrypt disable", cmd)

        lines = self.expect_command(self.ssh_manager.master_controller, "show wlan ssid-profile "
                                    + cmd.request_dict['target'] + " | include Passphrase", cmd)

        psk = None
        for line in lines:
            if line.startswith("WPA"):
                psk = line.replace("WPA Passphrase", "", 1).strip()
            if line.startswith("SSID Profile"):
                # """SSID Profile "fake_ssid_profile" undefined."""
                return "Error: SSID profile not defined.", 404

        _ = self.expect_command(self.ssh_manager.master_controller, "encrypt enable", cmd)

        return psk, 200

    def run_put_command(self, cmd: WellFormedCommand):
        length = len(cmd.request_dict['params']['psk'])
        if length < 8 or length > 63:
            return "Error: WPA passphrase must be 8-63 characters (check failed).", 400

        _ = self.expect_command(self.ssh_manager.master_controller, "configure t", cmd)

        _ = self.expect_command(self.ssh_manager.master_controller, "wlan ssid-profile " + cmd.request_dict['target'], cmd)

        lines  = self.expect_command(self.ssh_manager.master_controller, 'wpa-passphrase "'
                                     + cmd.request_dict['params']['psk'] + '"', cmd)

        for line in lines:
            if line.startswith("Error: WPA passphrase must be 8-63 characters."):
                # You see this if attempting to set a passphrase which is too short or long (for example).
                # This should have been handled by the earlier check, so 500 is appropriate.
                bonaire_functions.end_end(self, cmd)
                return "Server Error: WPA passphrase must be 8-63 characters (failed).", 500

        bonaire_functions.end_end(self, cmd)

        _ = self.expect_command(self.ssh_manager.master_controller, "write mem", cmd)

        return cmd.request_dict['params']['psk'], 204
