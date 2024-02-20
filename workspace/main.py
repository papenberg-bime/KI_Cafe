# this program is the main program for the whole task (Robot's movements, Camera, and results in GUI)

import threading
import queue
import traceback
import logging 
import sys
import os
import time 
from datetime import datetime

from helper.camera import Camera
from helper.robot import Robot
from helper.tool_assessment import ToolAssessment, tool_state_to_string
from helper.ai_csv import save_tool_states
from helper.ai_status import wait_for_ai
from helper.config import IMAGE_DIRECTORY, CSV_PATH, LOG_FILE_PATH
from helper.movement_paths import move_tool_to_cam, move_tool_to_slot

from classifier.predict import predict_image_list
from ui.ui import start_ui


def configure_logging():
  logging.basicConfig(level=logging.DEBUG, 
                      format="%(asctime)s [%(threadName)-12.12s] [%(name)-8.8s] [%(levelname)-5.5s]  %(message)s", 
                      handlers=[
                          logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
                          logging.StreamHandler(sys.stdout)
                      ],
                      )
  logging.getLogger("rtde").setLevel(logging.WARN)
  logging.getLogger("asyncio").setLevel(logging.WARN)
  logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARN)

configure_logging()
log = logging.getLogger("main")


thread_queue = queue.Queue()
shutdown = False
robot = None
# FIXME: Use sophisticated method to see if robot is ready
# this method will fail
while not robot:
    try:
        robot = Robot()
    except Exception as exception:
        wait_seconds = 30
        log.error("Exception ist aufgetreten ", exc_info=exception)
        print(f"Der Roboter ist nicht erreichbar. Bitte den Roboter über PolyScope starten. Nächster Verbindungsversuch in {wait_seconds} Sekunden. (Fehler: ", exception, ")\n")
        time.sleep(wait_seconds)

camera = Camera()
tool_assessments = []


def get_image_name(tool_number, picture_number):
    return f"{tool_number}_{picture_number}"

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def predict_in_thread(tool_number, write_to_ui):
    def predict():
        write_to_ui(f"KI startet mit Bewertung im Hintergrund für Tool {tool_number}...")
        log.debug(f"KI starts prediction for tool {tool_number}...")
        output_images = []
        for picture_number in range(8):
            output_images.append(tool_assessments[tool_number-1].get_image_paths(picture_number)["image_path"])

        prediction_results = predict_image_list(output_images)
        picture_number = 0
        for result in prediction_results:
            tool_assessments[tool_number-1].set_ai_assessment(picture_number, result['state'])
            picture_number+=1

        write_to_ui("KI-Bewertung für Werkzeug " + str(tool_number) + " abgeschlossen. Wurde von der KI bewertet mit: " + tool_state_to_string(tool_assessments[tool_number-1].get_overall_state()))
        log.debug(f"prediction for tool {tool_number} completed")
    ai_thread = threading.Thread(target = predict)
    ai_thread.start()


def thread_assess_tools():
    try:
        def write_to_ui(text):
            thread_queue.put(text)
                
        write_to_ui("Starte Prüflauf...")
        log.debug("starting new process")
        clear_assessments()
       
        for tool_number in range(1, 25):
            write_to_ui("Starte mit Werkzeug " + str(tool_number) + ".")
            log.debug("starting with tool " +str(tool_number))
            if not move_tool_to_cam(robot, tool_number, write_to_ui):
                write_to_ui("Kein Werkzeug gefunden in Slot " +str(tool_number) +", stoppe.")
                log.debug("no tool in slot " +str(tool_number))
                print("no tool... stopping")
                break
            robot.find_sensor_and_move_to_photo_position()
            
            turn_angle_in_degrees = 45
            for picture_number in range(8):
                rotation = turn_angle_in_degrees*picture_number
                robot.rotate_tool(rotation)
                
                filename = get_image_name(tool_number, picture_number) + '.png'
                image_path = os.path.join(IMAGE_DIRECTORY, f"{get_timestamp()}_{filename}" )
                image_path_high_resolution = os.path.join(IMAGE_DIRECTORY, 'HighResolution', filename)
            
                camera.take_photo(image_path, image_path_high_resolution)
                tool_assessments[tool_number-1].set_image_paths(picture_number, image_path, image_path_high_resolution, rotation)
                write_to_ui("Foto " + str(picture_number+1) + " erstellt.")
                log.debug("picture " + str(picture_number+1) + " created")
                
            predict_in_thread(tool_number, write_to_ui)
            move_tool_to_slot(robot, tool_number, write_to_ui)
                                                                                                                                                                                
            if shutdown:
                break
    except Exception as exception:
        log.error("Exception in process thread: ", exc_info=exception)
        write_to_ui("Ein Fehler ist aufgetreten, der Prüflauf wurde unterbrochen. Fehler: " + str(exception))

    finally:
        write_to_ui(None)

def save_csv():
    save_tool_states(tool_assessments, CSV_PATH)


def clear_assessments():
    for assessment in tool_assessments:
        assessment.clear()

if __name__ == '__main__':
    log.info("Program started.")

    for i in range(24):
        tool_assessments.append(ToolAssessment())

    print("Programm wartet darauf, dass die KI bereit ist (das sollte maximal 2 Minuten dauern)... Bitte warten!")
    log.info("Program waiting for starting ai")
    wait_for_ai()
    print("KI ist bereit!")
    log.info("ai initialized")

    def start_command():
        if not robot.is_in_remote_control():
            raise Exception("Roboter ist noch im Modus 'Local'. Bitte mit PolyScope auf 'Fernsteuerung' schalten.")

        # TODO: ensure that old thread was shut down
        save_csv()
        process_thread = threading.Thread(target = thread_assess_tools)
        process_thread.start()
        print("started")

    start_ui(start_command, thread_queue, tool_assessments, robot.dashboard)
    shutdown = True
    
    save_csv()
    log.info("save in csv")
    # exit and kill all threads:
    os._exit(0)
