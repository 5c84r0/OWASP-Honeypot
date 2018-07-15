#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import socket

from database.connector import insert_selected_modules_network_event
from database.connector import insert_other_network_event
from core.alert import info


def new_network_events(configuration):
    """
    get and submit new network events

    Args:
        configuration: user final configuration

    Returns:
        True
    """
    # start tshark as subprocess
    process = subprocess.Popen("tshark -Y \"ip.dst != {0}\" -T fields -e ip.dst -e tcp.srcport".format(
        socket.gethostbyname(socket.gethostname())), shell=True, stdout=subprocess.PIPE)
    # while True, read tshark output
    try:
        while True:
            line = process.stdout.readline()
            # check if new IP and Port printed
            if len(line) > 0:
                # split the IP and Port
                ip, port = line.rsplit()[0], int(line.rsplit()[1])
                # check if the port is in selected module
                inserted_flag = True
                for selected_module in configuration:
                    if port is configuration[selected_module]["real_machine_port_number"]:
                        # insert honeypot event (selected module)
                        insert_selected_modules_network_event(ip, port, selected_module)
                        inserted_flag = False
                if inserted_flag:
                    # insert common network event
                    insert_other_network_event(ip, port)
    except Exception as _:
        info(_)
    return True
