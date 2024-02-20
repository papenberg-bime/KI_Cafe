
from PIL import Image, ImageTk
from helper.tool_assessment import ToolAssessment, ToolState
import tkinter as tk
from tkinter import font


root = tk.Tk()
font = font.Font(family='Helvetica', name='appHighlightFont',
                 size=24, weight='bold')


COLORS = {
    "gut": "#70be51",
    "schlecht": "#eb6b40",
    "neutral": "#fcde67",
    "warnung": "#ffcccb",
}


def get_color_for_state():
    pass


def get_color_for_tool(tool: ToolAssessment):
    state = tool.get_overall_state()
    if state == ToolState.BAD:
        return COLORS["schlecht"]
    elif state == ToolState.RECYCLE:
        return COLORS["neutral"]
    elif state == ToolState.GOOD:
        return COLORS["gut"]
    else:
        return "gray"


def update_button_color(button, color):
    button.config(bg=COLORS[color])


def load_and_resize_image(path, scale_x, scale_y):
    original_image = Image.open(path)
    width, height = original_image.size
    new_width = int(width * scale_x)
    new_height = int(height * scale_y)
    resized_image = original_image.resize((new_width, new_height))
    return ImageTk.PhotoImage(resized_image)