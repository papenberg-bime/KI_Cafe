# Enthält die Steuerung für die Bewegungspfade und Code um diese Pfade zu testen.
from helper.robot import Robot
from helper.movement_paths_structure import movement_paths
#from helper.camera import Camera
import time


def execute_move_path(robot: Robot, waypoints, write_to_ui = None):
    index = 0
    while True:
        waypoint = waypoints[index]

        # print("Waypoint: " + str(waypoint))
        if str(waypoint).startswith("go_to_home"):
            print("  Going home")
            go_to_home(robot)
        elif str(waypoint).startswith("open_gripper"):
            print("  Opening gripper")
            robot.open_gripper()

            if robot.dashboard.is_faulty():
                if write_to_ui: 
                    write_to_ui("Roboter hat einen Fehler nach dem Öffnen. Programm versucht den Fehler selbst zu beheben, bitte warten!")
                robot.handle_fault()
                index += 1
                continue
        elif str(waypoint).startswith("close_gripper"):
            print("  Closing gripper")
            robot.close_gripper()
                
            if robot.dashboard.is_faulty():
                if write_to_ui: 
                    write_to_ui("Roboter hat einen Fehler nach dem Öffnen. Programm versucht den Fehler selbst zu beheben, bitte warten!")
                robot.handle_fault()
                index -= 2
                continue
        elif str(waypoint).startswith("move_from_home_to_sensor_finding_position"):
            go_to_home(robot)
            GRIPPER_CARRIES_NO_TOOL_THRESHOLD = 100
            if (robot.get_gripper_position() >= GRIPPER_CARRIES_NO_TOOL_THRESHOLD):
                robot.open_gripper()
                return False
            move_from_home_to_sensor_finding_position(robot)
        elif str(waypoint).startswith("move_from_sensor_finding_position_to_home"):
            move_from_sensor_finding_position_to_home(robot)
        else:
            robot.move(waypoint)

        index += 1
        if index == len(waypoints):
            break 

        # check for robot status
        if robot.dashboard.is_faulty():
            raise Exception("Der Roboter hat einen Fehler gemeldet. Der Prüflauf wurde unterbrochen.")

    return True


def move_to_sensor_finding_position(robot):
    robot.move("movel([3.146569166561159, -1.6334415120633832, 1.1443321129582193, 5.202630980183606, 4.715772313435802, -1.5711171752091753]")


def move_tool_to_cam(robot, tool_number, write_to_ui = None):
    if not execute_move_path(robot, movement_paths[f"tool{tool_number}_move_to_cam"], write_to_ui):
        return False
    move_to_sensor_finding_position(robot)
    return True


def move_tool_to_slot(robot, tool_number, write_to_ui = None):
    robot.move_down(0.1)
    execute_move_path(robot, movement_paths[f"tool{tool_number}_move_to_slot"], write_to_ui)


def go_to_home(robot):
    robot.move(
        "movej([3.2765653133392334, -1.7681886158385218, 2.0538347403155726, 1.2859884935566406, 4.701965808868408, -1.7445419470416468]")


def move_from_home_to_sensor_finding_position(robot):
    robot.move(
        "movel([3.275291681289673, -1.8411570988097132, 2.0547316710101526, 2.119201822871826, 4.623002052307129, -1.744376007710592]")
    robot.move(
        "movej([3.2365095615386963, -2.7150804005064906, 2.0822723547564905, 4.245496912593506, 4.677002429962158, -1.744528595601217]")
    robot.move(
        "movej([3.2403218746185303, -2.122820039788717, 1.33850604692568, 5.362422632962026, 4.671796798706055, -1.7443717161761683]")
    move_to_sensor_finding_position(robot)


def move_from_sensor_finding_position_to_home(robot):
    move_to_sensor_finding_position(robot)
    robot.move(
        "movej([3.2403218746185303, -2.122820039788717, 1.33850604692568, 5.362422632962026, 4.671796798706055, -1.7443717161761683]")
    robot.move(
        "movej([3.2365095615386963, -2.7150804005064906, 2.0822723547564905, 4.245496912593506, 4.677002429962158, -1.744528595601217]")
    robot.move(
        "movej([3.275291681289673, -1.8411570988097132, 2.0547316710101526, 2.119201822871826, 4.623002052307129, -1.744376007710592]")
    go_to_home(robot)




print("Starte Programm...")

if __name__ == '__main__':
    robot = Robot()
    #camera = Camera()

    #go_to_home(robot)
    #move_tool_to_cam(robot, 1)
    #robot.find_sensor_and_move_to_photo_position()
    #camera.take_photo("test.png", "test2.png")
    #move_tool_to_slot(robot, 1)
         
    go_to_home(robot)
    for i in range(1, 25):
        if not move_tool_to_cam(robot, i):
            break
    #    robot.find_sensor_and_move_to_photo_position()
        
    #    turn_angle_in_degrees = 45
    #    for picture_number in range(8):
    #        robot.rotate_tool(turn_angle_in_degrees*picture_number)
    #        camera.take_photo(file_suffix=str(
    #             i) + "_" + str(picture_number))
        move_tool_to_slot(robot, i)
