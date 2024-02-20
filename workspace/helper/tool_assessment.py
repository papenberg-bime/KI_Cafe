import random
from enum import Enum
import time

NUMBER_OF_PICTURES = 8


class ToolState(Enum):
    GOOD = 0
    BAD = 1
    RECYCLE = 2
    NONE = None


def tool_state_to_string(state: ToolState):
    if state == ToolState.GOOD:
        return "gut"
    elif state == ToolState.BAD:
        return "schlecht"
    elif state == ToolState.RECYCLE:
        return "aufbereiten"
    return "unbekannt"


class ToolAssessment:
    def __init__(self):
        self.ai_assessments = [None] * NUMBER_OF_PICTURES
        self.operator_assessments = [None] * NUMBER_OF_PICTURES
        self.images = [None] * NUMBER_OF_PICTURES

    def get_state(self, picture_number):
        operator_state = self.operator_assessments[picture_number]
        if operator_state != ToolState.NONE:
            return operator_state
        return self.ai_assessments[picture_number]

    def get_overall_state(self):
        all_states = []
        for picture_number in range(NUMBER_OF_PICTURES):
            all_states.append(self.get_state(picture_number))

        if ToolState.BAD in all_states:
            return ToolState.BAD
        if ToolState.RECYCLE in all_states:
            return ToolState.RECYCLE
        if ToolState.GOOD in all_states:
            return ToolState.GOOD
        return None

    def clear(self):
        for picture_number in range(NUMBER_OF_PICTURES):
            self.set_ai_assessment(picture_number, ToolState.NONE)
            self.set_operator_assessment(picture_number, ToolState.NONE)
            self.images[picture_number] = None

    def set_image_paths(self, number, image_path, image_path_high_resolution, rotation):
        self.images[number] = {
            'timestamp': time.time(),
            'rotation': rotation,
            'image_path': image_path,
            'image_path_high_resolution':image_path_high_resolution,
        }

    def get_image_paths(self, number):
        return self.images[number]

    def set_ai_assessment(self, number, state: ToolState):
        self.ai_assessments[number] = state

    def set_operator_assessment(self, number, state: ToolState):
        self.operator_assessments[number] = state

    def get_ai_assessment(self, number):
        return self.ai_assessments[number]

    def get_operator_assessment(self, number):
        return self.operator_assessments[number]


if __name__ == '__main__':
    tool = ToolAssessment()
    tool.set_ai_assessment(3, ToolState.BAD)
    tool.set_operator_assessment(3, ToolState.GOOD)
    tool.set_operator_assessment(4, ToolState.RECYCLE)
    print(tool.get_overall_state())