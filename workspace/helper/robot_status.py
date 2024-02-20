import logging
import sys

sys.path.append(".")
import vendor.rtde.rtde as rtde
import vendor.rtde.rtde_config as rtde_config
import time

# Socket settings:
RTDE_PORT = 30004
FREQUENCY = 250
CONFIG = "assets/record_configuration.xml"

ROBOT_STATE_STOPPED = 1
ROBOT_STATE_PLAYING = 2

def double_to_8bit(d):
    binary_str = bin(int(d))[2:].zfill(8)
    binary_array = [bool(int(bit)) for bit in binary_str]
    return binary_array[::-1]


def get_millisecond_time():
    return time.time_ns() / (1000 * 1000)

SAFETY_STATUS_OK = 1
SAFETY_STATUS_PROTECTIVE_STOP = 5

class RobotStatus:

    def __init__(self, HOST):
        self.robot_state = None
        self.con = None
        self.tool_positions = None
        self.joint_positions = None
        self.digital_inputs = None
        self.HOST = HOST
        self.init_connection()

    def init_connection(self):
        conf = rtde_config.ConfigFile(CONFIG)
        output_names, output_types = conf.get_recipe("out")

        con = rtde.RTDE(self.HOST, RTDE_PORT)
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
        self.con = con

    def disconnect(self):
        self.con.send_pause()
        self.con.disconnect()

    def get_robot_state(self):
        try:
            state = self.con.receive(False)
        except Exception: # rtde.RTDEException:
            print("rtde: Exception, trying to reconnect...")
            self.init_connection()
            state = self.con.receive(False)
            
        if state is not None:
            rtde_vars = state.__dict__
            self.digital_inputs = double_to_8bit(rtde_vars["actual_digital_input_bits"])
            self.joint_positions = rtde_vars["target_q"]
            self.tool_positions = rtde_vars["actual_TCP_pose"]
            self.robot_state = rtde_vars["runtime_state"]
            self.safety_status = rtde_vars["safety_status"]
            self.tcp_force = rtde_vars["actual_TCP_force"]
            return True
        else:
            print("State is None")
        return False

    def wait_robot_moving(self):
        count = 0
        MAX_WAIT = 1000
        start_time_in_milliseconds = get_millisecond_time()
        while True:
            if self.get_robot_state() and self.robot_state == ROBOT_STATE_PLAYING:
                break
            
            count += 1
            if (get_millisecond_time() - start_time_in_milliseconds) > MAX_WAIT:
                print(f"wait_robot_moving: Robot did not start moving in {MAX_WAIT/1000} second(s). Aborting wait.")
                break
            time.sleep(0.001)   # sleep 1ms for sync with robot controller (1000Hz)

    def wait_robot_moving_done(self):
        while True:
            if self.get_robot_state() and self.robot_state == ROBOT_STATE_STOPPED:
                break
            time.sleep(0.001)   # sleep 1ms for sync with robot controller (1000Hz)

    def wait_for_robot(self):
        self.wait_robot_moving()
        self.wait_robot_moving_done()

    def get_digital_input(self, index: int) -> bool:
        self.get_robot_state()
        return self.digital_inputs[index]

    def get_joint_positions(self):
        self.get_robot_state()
        return self.joint_positions

    def get_tool_positions(self):
        self.get_robot_state()
        return self.tool_positions

    def get_tcp_force(self):
        self.get_robot_state()
        return self.tcp_force


