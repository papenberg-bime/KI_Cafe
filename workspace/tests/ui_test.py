import threading
import queue
import sys
sys.path.append('.')
from ui.ui import start_ui
from helper.tool_assessment import ToolAssessment, tool_state_to_string

thread_queue = queue.Queue()
tool_assessments = [ToolAssessment() for _ in range(24)]

path_prefix ="D:/Storage/"

all_paths = [
    ["20231213_141956_1_0.png", "HighResolution/1_0.png"],
    ["20231213_142000_1_1.png", "HighResolution/1_1.png"],
    ["20231213_142004_1_2.png", "HighResolution/1_2.png"],
    ["20231213_142007_1_3.png", "HighResolution/1_3.png"],
    ["20231213_142011_1_4.png", "HighResolution/1_4.png"],
    ["20231213_142014_1_5.png", "HighResolution/1_5.png"],
    ["20231213_142018_1_6.png", "HighResolution/1_6.png"],
    ["20231213_142021_1_7.png", "HighResolution/1_7.png"],
]

for picture_number, paths in enumerate(all_paths):
    tool_assessments[0].set_image_paths(picture_number, path_prefix + paths[0], path_prefix + paths[1], picture_number*45)

if __name__ == '__main__':
    def start_command():
        print("Start...")

    start_ui(start_command, thread_queue, tool_assessments)