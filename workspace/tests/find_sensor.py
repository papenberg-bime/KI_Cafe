import sys
sys.path.append('.')
from helper import robot_control as rc
from helper.robot import Robot

robot = None


def test_find_sensor():
    robot.move(
        "movej([3.161489407062528, -1.6180947495239428, 1.1552334318950468, 5.199161308765908, 4.689699700108763, 0.04991641660703782]")
    z_step = 0.001
    robot.find_tool_sensor(z_step)

if __name__ == '__main__':
    robot = Robot()
    test_find_sensor()
