import sys
sys.path.append('.')
from helper import robot_control as rc
from helper import movement
from helper import connection

if __name__ == '__main__':
    rt_socket = connection.get_connection_to_robot()

    robot_status.wait_robot_moving_done(rt_socket)

    turn_angle = 45     # in degrees
    for i in range(8):
        movement.rotate_tool(turn_angle*i, rt_socket)
