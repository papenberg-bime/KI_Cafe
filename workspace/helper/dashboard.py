import socket
import time 

PORT = 29999

CMD_IS_IN_REMOTE_CONTROL = "is in remote control"
IS_IN_REMOTE_CONTROL_TRUE = "true"
IS_IN_REMOTE_CONTROL_FALSE = "false"

CMD_GET_SAFETY_STATUS = "safetystatus"
SAFETY_STATUS_NORMAL = "NORMAL"
SAFETY_STATUS_FAULT = "FAULT"
SAFETY_STATUS_SAFEGUARD_STOP = "SAFEGUARD_STOP"
SAFETY_STATUS_PROTECTIVE_STOP = "PROTECTIVE_STOP" # roboter einfach wieder aktivierbar

CMD_GET_ROBOTMODE = "robotmode"
ROBOTMODE_RUNNING = "RUNNING"
ROBOTMODE_POWER_OFF = "POWER_OFF"
ROBOTMODE_IDLE = "IDLE"

CMD_CLOSE_SAFETY_POPUP = "close safety popup"
CMD_RESTART_SAFETY = "restart safety"
CMD_POWER_ON = "power on"
CMD_BRAKE_RELEASE = "brake release"

class Dashboard:

    def __init__(self, HOST):
        self.host = HOST

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, PORT))
        connected = self.socket.recv(1024).decode('utf-8')
        if 'Connected' not in connected:
            raise Exception("Dashboard: Could not connect to Dashboard Server!")

    def send_command(self, command: str) -> str:
        self.connect()
        command = command + "\n"
        self.socket.send(command.encode('utf-8'))
        response = self.socket.recv(1024).decode('utf-8')
        self.close_connection()
        return response

    def close_connection(self):
        self.socket.close()

    def is_in_remote_control(self):
        response = self.send_command(CMD_IS_IN_REMOTE_CONTROL)
        return IS_IN_REMOTE_CONTROL_TRUE in response

    def is_faulty(self):
        safety_response = self.send_command(CMD_GET_SAFETY_STATUS)
        robot_mode_response = self.send_command(CMD_GET_ROBOTMODE)
        if SAFETY_STATUS_NORMAL not in safety_response or ROBOTMODE_RUNNING not in robot_mode_response:
            return True
        return False
    
    def wait_for_status(self, command, status):
        n = 0
        while True:
            response = self.send_command(command)
            time.sleep(1)
            n += 1
            if status in response:
                # print("Ready!")
                break
            if n > 60:
                raise Exception(f"dashboard: wait_for_status({command},{status}): Timeout (was {response})")
                

    def get_safety_status(self):
        return self.send_command(CMD_GET_SAFETY_STATUS)
    

    def handle_fault(self):
        try:
            response = self.send_command(CMD_CLOSE_SAFETY_POPUP)
            print("  Closing safety popup...", response)
            
            if SAFETY_STATUS_NORMAL not in self.send_command(CMD_GET_SAFETY_STATUS):
                response = self.send_command(CMD_RESTART_SAFETY)
                print("  Restarting Safety...", response)
                self.wait_for_status(CMD_GET_SAFETY_STATUS, SAFETY_STATUS_NORMAL)
 
            response = self.send_command(CMD_POWER_ON)
            print("  Power on...", response)

            self.wait_for_status(CMD_GET_ROBOTMODE, ROBOTMODE_IDLE)
 
            response = self.send_command(CMD_BRAKE_RELEASE)
            print("  Releasing brakes...", response)
            
            self.wait_for_status(CMD_GET_ROBOTMODE, ROBOTMODE_RUNNING)
        except Exception as e:
            print("Exception: ", e)
        
