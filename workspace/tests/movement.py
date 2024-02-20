# Testing general movement with 3 waypoints
import sys
sys.path.append('.')
from helper.robot_control import wait_for_robot
from helper import connection

if __name__ == '__main__':
    rt_socket = connection.get_connection_to_robot()

    rt_socket.send(
        ("movej([3.334277003009967, -1.8085101709165243, 1.8554595277951718, 1.8688985630355281, 4.364195794611821, -1.805194045337735], a=6, v=6)\n").encode("utf8"))
    wait_for_robot()

    rt_socket.send(
        ("movej([3.334277003009967, -1.8085101709165243, 1.8554595277951718, 2.4083798348269756, 4.364195794611821, -1.805194045337735], a=6, v=6)\n").encode("utf8"))
    wait_for_robot()

    rt_socket.send(
        ("movej([3.335149667635964, -2.1722367870321424, 1.845860216909203, 1.8425440913304136, 4.572239041449546, -1.805194045337735], a=6, v=6)\n").encode("utf8"))
    wait_for_robot()
