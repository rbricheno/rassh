"""This contains various functions used to compose the Bonaire API SSH commands."""
import re
from typing import Optional

from rassh.datatypes import WellFormedCommand
from rassh.exceptions.exception_with_status import ExceptionWithStatus


def set_group(ssh_command, ap_wiredmac: str, ap_group: str, cmd: WellFormedCommand):
    lines = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                    "whitelist-db rap modify mac-address " + ap_wiredmac + " ap-group "
                                       + ap_group, cmd)

    for line in lines:
        if line.startswith("Entry Does not Exist"):
            _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                        "whitelist-db rap add mac-address " + ap_wiredmac
                                           + " ap-group " + ap_group, cmd)
    lines = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                    "ap-regroup wired-mac " + ap_wiredmac + " " + ap_group, cmd)

    if lines:
        for line in lines:
            if line.startswith("AP with MAC"):
                # Might say "AP with MAC address PP:QQ:RR:SS:TT:UU not found."
                # This means the AP was not found on the controller.
                raise ExceptionWithStatus("Error: AP not found on controller when setting group.", 500)
            elif line.startswith("NOTE: For cert RAP ap-group specified in RAP whitelist will take precedence"):
                # You will see this line even if the group name is completely fictitious, no error is shown.
                # This is as close as we ever get to knowing it was a success. Return (without an exception).
                return
        # TODO Is this correct? Or will RAP show "AP with MAC address ..."
        raise ExceptionWithStatus("Error: Unexpected output when setting group.", 500)
    # TODO is this actually an error? Can you ever set a group and *not* see "NOTE: ..."?
    raise ExceptionWithStatus("Error: No output when setting group.", 500)


def reprovision_remote(ssh_command, remote_ap: int, cmd: WellFormedCommand):
    if remote_ap == 1:
        _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller, "remote ap", cmd)
    else:
        _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller, "no remote ap", cmd)


def enter_provisioning_mode(ssh_command, cmd: WellFormedCommand):
    _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller, "configure t", cmd)
    _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller, "provision-ap", cmd)


def end_end(ssh_command, cmd: WellFormedCommand):
    _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller, "end", cmd)
    _ = ssh_command.expect_command(ssh_command.ssh_manager.master_controller, "end", cmd)


def reprovision_or_enqueue(ssh_command, request: str, ap_wiredmac: str, cmd: WellFormedCommand):
    """If an AP is down when attempting to reprovision, postpone the reprovisioning (and other actions).
       Run this command near the start of the process so we can fail (enqueue) early."""
    lines = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                    "read-bootinfo wired-mac " + ap_wiredmac, cmd)

    for line in lines:
        if line.startswith("AP with MAC"):
            # Might say "AP with MAC address PP:QQ:RR:SS:TT:UU not found."
            # This means the AP was not found on the controller.
            raise ExceptionWithStatus("Error: AP was not found on the controller when reprovisioning.", 500)
        if line.startswith("AP is down"):
            # Enqueue the entire provisioning task until the AP is up.
            enqueue_status = ssh_command.ssh_manager.queue.enqueue_request(request)
            if enqueue_status:
                raise ExceptionWithStatus("AP is down, command has been enqueued.", 202)
            else:
                raise ExceptionWithStatus("Error: AP is down and command could not be enqueued because of"
                                          + "a queue error.", 500)


def get_lms_ip_and_ap_status(ssh_command, ap_wiredmac: str, cmd: WellFormedCommand) -> (Optional[str], str):
    """Get the IP of the LMS that knows more about this AP."""
    lines = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                    "show ap details wired-mac " + ap_wiredmac, cmd)

    lms = None
    ap_status = "Down"
    for line in lines:
        if line.startswith("LMS"):
            parts = line.split()
            try:
                lms = parts[3]
            except IndexError:
                raise ExceptionWithStatus("Could not parse LMS IP.", 500)
        if line.startswith("Status"):
            parts = line.split()
            try:
                ap_status = parts[1]
            except IndexError:
                raise ExceptionWithStatus("Could not parse AP status.", 500)
        # Might say """AP with MAC address PP:QQ:RR:SS:TT:UU not found."""
        if line.startswith("AP with MAC "):
            raise ExceptionWithStatus("AP not found on master when getting LMS.", 404)

    return lms, ap_status


def get_lms_ip_and_connect_lms(ssh_command, ap_wiredmac: str, cmd: WellFormedCommand) -> str:
    """Connect to the IP of the LMS that knows more about this AP. Use this as a prelude to running LMS commands.
    Includes some helpful exceptions so we know not to proceed with configuration if LMS is unavailable."""
    lms, ap_status = get_lms_ip_and_ap_status(ssh_command, ap_wiredmac, cmd)
    if ap_status == "Down":
        raise ExceptionWithStatus("AP is down, cannot proceed.", 412)
    if lms is None:
        raise ExceptionWithStatus("No LMS found for this AP.", 404)

    # Dynamically add an LMS if it is not already known (we may not have connected to it before).
    if lms not in ssh_command.ssh_manager.switches:
        ssh_command.ssh_manager.lms_ssh_connections[lms] = ssh_command.ssh_manager.get_new_expect_connection(lms)

    # Get back to the "enable" prompt, in case something went wrong the last time we used this LMS.
    _ = ssh_command.expect_command(lms, "end", cmd)
    _ = ssh_command.expect_command(lms, "end", cmd)

    return lms


def get_ap_name(ssh_command, ap_wiredmac: str, cmd: WellFormedCommand) -> str:
    """Get the name of this AP from its wired MAC."""
    lines = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                    "show ap details wired-mac " + ap_wiredmac + " | include Basic", cmd)

    ap_name = None
    for line in lines:
        if line.startswith("AP"):
            groups = re.findall(r'AP "(.*)" Basic Information', line)
            try:
                ap_name = groups[0]
                break
            except IndexError:
                raise ExceptionWithStatus("Could not parse AP name.", 500)
    if not ap_name:
        raise ExceptionWithStatus("AP name not found for this wired MAC.", 404)
    return ap_name


def get_group(ssh_command, ap_wiredmac: str, cmd: WellFormedCommand) -> Optional[str]:
    lines = ssh_command.expect_command(ssh_command.ssh_manager.master_controller,
                                    "show ap details wired-mac " + ap_wiredmac + " | include Group", cmd)

    group = None
    for line in lines:
        if line.startswith("Group"):
            parts = line.split()
            try:
                group = parts[1]
            except IndexError:
                raise ExceptionWithStatus("Could not parse group name from controller output.", 500)
        if line.startswith("AP with MAC"):
            # """AP with MAC address PP:QQ:RR:SS:TT:UU not found."""
            raise ExceptionWithStatus("AP not found when getting group.", 404)

    return group


def lms_get_gains(ssh_command, lms: str, ap_wiredmac: str, cmd: WellFormedCommand) -> tuple:
    lines = ssh_command.expect_command(lms, "show ap provisioning wired-mac " + ap_wiredmac
                                       + ' | include "gain for 802.11"', cmd)

    a_ant_gain = None
    g_ant_gain = None
    for line in lines:
        # Might say """AP is not registered with this switch"""
        if line.startswith("AP is not registered with this switch"):
            raise ExceptionWithStatus("AP not registered on LMS when getting gains.", 404)
        # Might say """AP with MAC address PP:QQ:RR:SS:TT:UU not found."""
        if line.startswith("AP with MAC "):
            raise ExceptionWithStatus("AP not found on LMS when getting gains.", 404)

        if line.startswith("Antenna gain for 802.11a"):
            parts = line.split()
            try:
                if parts[4] == "N/A":
                    a_ant_gain = None
                else:
                    a_ant_gain = parts[4]
            except IndexError:
                raise ExceptionWithStatus("Could not parse antenna gain (a) from controller output.", 500)
        if line.startswith("Antenna gain for 802.11g"):
            parts = line.split()
            try:
                if parts[4] == "N/A":
                    g_ant_gain = None
                else:
                    g_ant_gain = parts[4]
            except IndexError:
                raise ExceptionWithStatus("Could not parse antenna gain (g) from controller output.", 500)

    return (a_ant_gain, g_ant_gain)


def lms_get_remote_ap(ssh_command, lms: str, ap_wiredmac: str, cmd: WellFormedCommand) -> Optional[int]:

    lines = ssh_command.expect_command(lms, "show ap provisioning wired-mac " + ap_wiredmac
                                       + ' | include "Remote AP"', cmd)

    remote_ap = None
    for line in lines:
        # Might say """AP is not registered with this switch"""
        if line.startswith("AP is not registered with this switch"):
            raise ExceptionWithStatus("AP not registered on LMS when getting remote AP.", 404)
        # Might say """AP with MAC address PP:QQ:RR:SS:TT:UU not found."""
        if line.startswith("AP with MAC "):
            raise ExceptionWithStatus("AP not found on LMS when getting remote AP.", 404)

        if line.startswith("Remote AP"):
            parts = line.split()
            try:
                if parts[2] == "No":
                    remote_ap = 0
                elif parts[2] == "Yes":
                    remote_ap = 1
                else:
                    raise ExceptionWithStatus("Could not recognise remote AP from controller output.", 500)
            except IndexError:
                raise ExceptionWithStatus("Could not parse remote AP from controller output.", 500)

    return remote_ap


def get_remote_ap(ssh_command, ap_wiredmac, cmd: WellFormedCommand) -> int:
    lms = get_lms_ip_and_connect_lms(ssh_command, ap_wiredmac, cmd)
    remote_ap = lms_get_remote_ap(ssh_command, lms, ap_wiredmac, cmd)
    return remote_ap


def get_gains(ssh_command, ap_wiredmac, cmd: WellFormedCommand) -> tuple:
    lms = get_lms_ip_and_connect_lms(ssh_command, ap_wiredmac, cmd)
    gains = lms_get_gains(ssh_command, lms, ap_wiredmac, cmd)
    return gains


def get_gains_and_remote_ap(ssh_command, ap_wiredmac, cmd: WellFormedCommand) -> dict:
    lms = get_lms_ip_and_connect_lms(ssh_command, ap_wiredmac, cmd)
    gains = lms_get_gains(ssh_command, lms, ap_wiredmac, cmd)
    remote_ap = lms_get_remote_ap(ssh_command, lms, ap_wiredmac, cmd)
    return {"gains": gains, "remote_ap": remote_ap}
