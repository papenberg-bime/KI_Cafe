import math
import time
import socket
from helper.robot_status import RobotStatus
from helper.dashboard import Dashboard
from helper.gripper_status import GripperStatus
from helper.config import HOST
import logging

PORT = 30003

SCRIPT_PATH         = "assets/URScripts/"
OPEN_SCRIPT         = SCRIPT_PATH + "open.script"
CLOSE_SCRIPT        = SCRIPT_PATH + "close.script"
ACTIVATE_SCRIPT     = SCRIPT_PATH + "activate.script"
FORCE_ACTIVATE_SCRIPT = SCRIPT_PATH + "force_activate.script"
AUTO_RELEASE_SCRIPT = SCRIPT_PATH + "auto_release.script"

ACCELERATION = 2
VELOCITY = 2

log = logging.getLogger("robot")

class Robot:

    def __init__(self):
        self.connect()
        self.robot_status = RobotStatus(HOST)
        self.dashboard = Dashboard(HOST)
        self.gripper_status = GripperStatus(HOST)
        time.sleep(0.1)

    def connect(self):
        self.rt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rt_socket.connect((HOST, PORT))

    def get_robot_status(self):
        return self.robot_status
    
    def is_in_remote_control(self):
        return self.dashboard.is_in_remote_control()

    def find_sensor_and_move_to_photo_position(self):        
        self.find_tool_sensor(z_step=0.001)
        # ATTENTION: Change here, if the mirror or camera position had been changed
        # Move 6.5 mm down (on the z axis)
        self.move_down(0.0065)
        # 7.5mm to the left (positive x is to the left, negative to the right), 
        # and 3.166cm towards the camera (negative y is towoards the cam, positive away from the cam)
        self.move_relative(x=0.0075, y=-0.03166)    
        
    def wait_movement_finished(self):
        self.robot_status.wait_for_robot()

    def wait_moving_done(self):
        self.robot_status.wait_robot_moving_done()

    def rotate_tool(self, angle: float):
        turn_position = self.robot_status.get_joint_positions()
        turn_position[5] = math.radians(angle)
        turn_position[5] %= math.pi*2
        self.move("movej(" + str(turn_position),  2, 2)

    # speed is critical, low speed will lead to wrong movement in other axes (e.g. 0.0025 will fail)
    def find_tool_sensor(self, z_step: float = 0.001):
        position = self.robot_status.get_tool_positions()
        while True:
            if self.robot_status.get_digital_input(0):
                return True
            print('.', end='')
            # Move z axis [2] toward sensor
            position[2] -= z_step
            self.move(
                "movej(get_inverse_kin(p" + str(position)+")", 1, 2)


    def close_gripper(self):
        self.send_file(CLOSE_SCRIPT)

    def open_gripper(self):
        self.send_file(OPEN_SCRIPT)

    def activate_gripper(self):
        self.send_file(ACTIVATE_SCRIPT)

    def force_activate_gripper(self):
        self.send_file(FORCE_ACTIVATE_SCRIPT)

    def auto_release_gripper(self):
        self.send_file(AUTO_RELEASE_SCRIPT)

    def send_file(self, filename):
        f = open(filename, "rb")
        chunk = f.read(1024)
        while (chunk):
            try:
                self.rt_socket.send(chunk)
            except Exception as ex:
                print("Exception in move: ", ex)
                self.connect()
                self.rt_socket.send(chunk)

            chunk = f.read(1024)
        time.sleep(1)

    def move(self, command, acceleration=ACCELERATION, velocity=VELOCITY):
        if str(command).endswith(']'):
            command += f",a={acceleration}, v={velocity}"
        final_command = (command + ")\n").encode('utf8')
        try:
            self.rt_socket.send(final_command)
        except Exception as ex:
            print("Exception in move: ", ex)
            self.connect()
            self.rt_socket.send(final_command)

        self.robot_status.wait_for_robot()


    def move_down(self, amount):
        self.move_relative(z=amount)


    def move_relative(self, x: float = 0, y: float = 0, z: float = 0, rx: float = 0, ry: float = 0, rz: float = 0):
        current_position = self.robot_status.get_tool_positions()
        current_position[0] += x
        current_position[1] += y
        current_position[2] += z

        current_position[3] += rx
        current_position[4] += ry
        current_position[5] += rz

        self.move("movej(get_inverse_kin(p" + str(current_position) +
                  ")", 0.5, 0.1)
        
        
    def get_gripper_position(self):
        return self.gripper_status.get_position()
    

    def handle_fault(self):
        log.error("Handle fault called.")
        print("Handle Fault")
        time.sleep(5)
        self.dashboard.handle_fault()
        if self.dashboard.is_faulty():
            raise Exception("Fehler konnte nicht automatisch behoben werden")
        self.move_down(-0.003)
        print("Position", self.get_gripper_position())
        self.auto_release_gripper()
        print("Position", self.get_gripper_position())

        self.move_down(-0.15)
        self.activate_gripper()
        time.sleep(1)
        self.open_gripper()  
        if self.dashboard.is_faulty():
            raise Exception("Fehler konnte nicht automatisch behoben werden")
           
 