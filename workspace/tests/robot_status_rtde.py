#!/usr/bin/env python
# Copyright (c) 2020-2022, Universal Robots A/S,
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Universal Robots A/S nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL UNIVERSAL ROBOTS A/S BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# https://github.com/UniversalRobots/RTDE_Python_Client_Library

import logging
import sys

sys.path.append(".")
import vendor.rtde.rtde as rtde
import vendor.rtde.rtde_config as rtde_config

HOST = "169.254.46.85"
PORT = 30004
FREQUENCY = 10
CONFIG = "assets/record_configuration.xml"

#if args.verbose:
#    logging.basicConfig(level=logging.INFO)

conf = rtde_config.ConfigFile(CONFIG)
output_names, output_types = conf.get_recipe("out")

con = rtde.RTDE(HOST, PORT)
con.connect()

# get controller version
print("Version: " + str(con.get_controller_version()))

# setup recipes
if not con.send_output_setup(output_names, output_types, frequency=FREQUENCY):
    logging.error("Unable to configure output")
    sys.exit()

# start data synchronization
if not con.send_start():
    logging.error("Unable to start synchronization")
    sys.exit()

def double_to_8bit(d):
    binary_str = bin(int(d))[2:].zfill(8)
    binary_array = [bool(int(bit)) for bit in binary_str]
    return binary_array[::-1]

keep_running = True
while keep_running:

    try:
        state = con.receive(False)
        if state is not None:
            vars = state.__dict__
            digital_inputs = double_to_8bit(vars["actual_digital_input_bits"])
            # print(vars["timestamp"], vars["target_q"], vars["robot_mode"], vars["runtime_state"])
            print( vars["target_q"], vars["actual_TCP_pose"], digital_inputs[0], vars["runtime_state"], vars["safety_status"])
            # target q = get joint positions
            # actual_TCP_pose = get_tool_positions
            # robot_mode = state ()
            # https://s3-eu-west-1.amazonaws.com/ur-support-site/22229/Real_Time_Data_Exchange_(RTDE)_Guide.pdf

            # Safety States:
            # 9 - critical error
            # See: https://forum.universal-robots.com/t/what-are-the-values-of-robot-safety-status-in-rtde/29904

            # Robot States: 
            # Stopping : 0
            # Stopped : 1
            # Playing : 2
            # Pausing : 3
            # Paused : 4
            # Resuming : 5
            # See: https://forum.universal-robots.com/t/rtde-runtime-state-enumeration/6634/2

            # https://s3-eu-west-1.amazonaws.com/ur-support-site/42728/DashboardServer_e-Series_2022.pdf
            # https://www.universal-robots.com/articles/ur/interface-communication/overview-of-client-interfaces/
                      
    except KeyboardInterrupt:
        keep_running = False
    except rtde.RTDEException:
        con.disconnect()
        sys.exit()

print("Disconnecting...")
con.send_pause()
con.disconnect()
