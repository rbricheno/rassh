import re
from rassh.commands.ssh_bonaire_command_base import SSHBonaireCommandBase
from rassh.commands import bonaire_functions
from rassh.datatypes.well_formed_command import WellFormedCommand


class SSHBonaireBLE(SSHBonaireCommandBase):

    def __init__(self, expect_manager):
        SSHBonaireCommandBase.__init__(self, expect_manager)
        self.object_type = 'ap'
        self.command_name = 'ble'
        self.payload = []

    def run_get_command(self, cmd: WellFormedCommand):
        """Get the MAC address of the Bluetooth Low Energy beacons in this AP."""
        mac_matcher = re.compile('([\da-f]{2}(?:[-:][\da-f]{2}){5})')

        ap_name = bonaire_functions.get_ap_name(self, cmd.request_dict['target'], cmd)

        lms = bonaire_functions.get_lms_ip_and_connect_lms(self, cmd.request_dict['target'], cmd)

        ble_macs = []
        lines = self.expect_command(lms, "show ap debug ble-table ap-name " + ap_name + " all", cmd)

        for line in lines:
            if line.startswith("No AP found with"):
                return "AP not found on LMS", 412
            mac_matched = mac_matcher.match(line)
            if mac_matched:
                mac = mac_matched.group(0)
                ble_macs.append(mac)
        return ble_macs, 200

    def run_put_command(self, cmd: WellFormedCommand):
        # Not implemented by the host system.
        return "Not implemented.", 501
