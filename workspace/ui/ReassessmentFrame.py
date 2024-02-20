import os
import tkinter as tk
from ui.ImageReassessmentComponent import create_image_reassessment_component
from ui.Common import root, font
from helper.tool_assessment import ToolAssessment, ToolState, NUMBER_OF_PICTURES


def open_reassessment_frame(tool_number, tool, update_overview_tool_buttons, add_line_to_log_output):
    modal = tk.Toplevel(root)
    modal.overrideredirect(True)
    modal.geometry(
        "{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    title_text = f"Nachbewertung von Werkzeug {tool_number}"
    modal.title(title_text)

    title = tk.Label(modal, text=title_text, font=font)
    title.grid(row=0, column=0)

    def close_reassessment():
        update_overview_tool_buttons()
        modal.destroy()

    back_button = tk.Button(modal, text="zurück", height=1, command=close_reassessment, font=font, relief="solid")
    back_button.grid(row=0, column=3, sticky='nsew')
    modal.grid_rowconfigure(1, weight=1)

    update_methods = []

    def update_all():
        for update_method in update_methods:
            update_method()


    frame = tk.Frame(modal)
    frame.grid(row=1, column=0, columnspan=4, sticky='nsew')
    for row in range(0, 2):
        for column in range(4):
            image_number = row * 4 + column
            image_path = tool.get_image_paths(image_number)["image_path"]
            if os.path.exists(image_path):
                update_method = create_image_reassessment_component(
                    frame, image_path, row * 2, column, tool, image_number, tool_number, update_all)  
                update_methods.append(update_method)            
            else:
                break

    def confirm_ai_predictions():
        for picture_number in range(NUMBER_OF_PICTURES):
            ai_state = tool.get_ai_assessment(picture_number)
            if tool.get_operator_assessment(picture_number) == ToolState.NONE:
                tool.set_operator_assessment(picture_number, ai_state)
        add_line_to_log_output(f"Alle ausgewählten Bewertungen für Werkzeug {tool_number} wurden als korrekt bestätigt.")
        close_reassessment()

    confirm_ai_button = tk.Button(modal, text="Alle ausgewählten Bewertungen als korrekt bestätigen", height=1, command=confirm_ai_predictions, font=font, relief="solid")
    confirm_ai_button.grid(row=3, column=3, sticky='nsew', pady=(0, 150))
