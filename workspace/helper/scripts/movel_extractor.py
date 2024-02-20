import sys
sys.path.append('.')
from helper.robot import Robot

robot = None

if __name__ == '__main__':
    robot = Robot()

    try:    
        while True:
    
            position = robot.get_robot_status().get_joint_positions()
            tcp_force = robot.get_robot_status().get_tcp_force()
            print('robot.move("movel(' + str(position) + '")' )
            print('tcp_force', tcp_force)
            input()

    except KeyboardInterrupt:
        pass
    