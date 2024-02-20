import sys
sys.path.append('.')
from helper.robot import Robot


def gripper_test():
    robot.move("movel([3.2739504817290075, -1.7022186374076576, 1.2350801769296043, 2.0255857251769562, 4.711516261798119, -1.697302502704547]",)
    robot.move("movel([3.2738384277382337, -1.6822307166067878, 1.1691973116645666, 2.07147971395318, 4.711727500533998, -1.6970044707929297]",)
    
    n = 0
    while True:
        def process_fault():
            nonlocal n
            robot.handle_fault()
            robot.move("movel([3.2739504817290075, -1.7022186374076576, 1.2350801769296043, 2.0255857251769562, 4.711516261798119, -1.697302502704547]",)
            robot.move("movel([3.2738384277382337, -1.6822307166067878, 1.1691973116645666, 2.07147971395318, 4.711727500533998, -1.6970044707929297]",)
            n = 0

        robot.close_gripper()
        if robot.dashboard.is_faulty():
            print("Error after close", n)
            process_fault()    
        
        robot.open_gripper()
        if robot.dashboard.is_faulty():
            print("Error after open", n)
            process_fault()
            
        n += 1

if __name__ == '__main__':
    robot = Robot()
    gripper_test()