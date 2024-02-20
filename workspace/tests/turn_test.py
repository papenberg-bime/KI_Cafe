import socket
import time
import math
import helper.robot_control as rc

# socket realtime connection
rt_socket = None

####### Socket settings:
HOST= "169.254.46.85"
PORT= 30003

def turn_tool(angle : float):
    turn_position = rc.get_joint_positions()
    turn_position[5] = math.radians(angle) 
    turn_position[5] %= math.pi*2
    print("Turn: "+str(math.degrees(turn_position[5])))
    rt_socket.send(("movej(" + str(turn_position) + ", a=1, v=1)" + "\n").encode('utf8'))
    rc.wait_robot_moving(rt_socket)
    rc.wait_robot_moving_done(rt_socket)

if __name__ == '__main__':
    # Connect to robot
    rt_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    rt_socket.connect((HOST, PORT))
    time.sleep(0.1)

    rc.wait_robot_moving_done(rt_socket)

    turn_angle = 45     # in degrees
    for i in range(8):     
        turn_tool(turn_angle*i) # turn tool
