import sys
import logging
import tkinter as tk
from tkinter import font, messagebox
from datetime import datetime
import queue
sys.path.append('.')
from ui.Common import root, font, get_color_for_tool, COLORS
from ui.ReassessmentFrame import open_reassessment_frame
from helper.tool_assessment import ToolAssessment, ToolState
from helper.dashboard import Dashboard, SAFETY_STATUS_NORMAL, SAFETY_STATUS_SAFEGUARD_STOP


log = logging.getLogger("ui")



loaded_images = []
overview_tool_buttons = []
log_output = None
tool_assessments = None
tool_positions = {
        'left': [
            [3, 2, 1],
            [4, 5, 6],
            [9, 8, 7],
            [10, 11, 12]
        ],
        'right': [
            [13, 14, 15],
            [18, 17, 16],
            [19, 20, 21],
            [24, 23, 22]
        ]
    }


def add_line_to_log_output(text):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_output.insert(chars=f"{timestamp} {text}\n", index="end")
    log_output.yview_scroll(1000, what="pages")


def is_tool_ready(tool: ToolAssessment):
    return tool.get_image_paths(7) and tool.get_ai_assessment(7) != ToolState.NONE


def update_overview_tool_buttons():
    for button in overview_tool_buttons:
        color = get_color_for_tool(button.tool)
        button.config(bg=color)

        if is_tool_ready(button.tool):
            button.config(command=lambda
                          tool_number=button.tool_number,
                          tool=button.tool,
                          update=update_overview_tool_buttons:
                          open_reassessment_frame(tool_number, tool, update, add_line_to_log_output),
                          state=tk.NORMAL, bg=color)
        else:
            button.config(state=tk.DISABLED, bg=color)


def start_ui(start_command, thread_queue, assessments, robot_dashboard: Dashboard):
    global log_output
    global tool_assessments
    tool_assessments = assessments
    root.overrideredirect(True)
    log.info("UI started.")

    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(),
                                    root.winfo_screenheight()))
    root.title("Prüfstand")

    for row in range(4):
        for column in range(3):
            tool_number_left = tool_positions['left'][row][column]
            tool_number_right = tool_positions['right'][row][column]

            def create_button(tool_number, row, column):
                tool = tool_assessments[tool_number - 1]
                button = tk.Button(root, font=font,
                                text=f"Werkzeug {tool_number}", relief="solid", border=1)
                button.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
                button.tool_number = tool_number
                button.tool = tool
                return button

            overview_tool_buttons.append(create_button(tool_number_left, row, column))
            overview_tool_buttons.append(create_button(tool_number_right, row, column + 4 + 1))

    update_overview_tool_buttons()

    log_output = tk.Text(root, width=10, height=10)
    log_output.grid(column=0, row=4, columnspan=3,
            rowspan=4, padx=5, pady=5, sticky='nsew')

    frame = tk.Frame(root, border=0, width=100, height=100)  # relief="groove"
    frame.grid(column=5, row=4, columnspan=3, padx=5, pady=5, sticky='nsew')

    def start_pressed():
        try:
            print( "Safety status: ", robot_dashboard.get_safety_status())
            if SAFETY_STATUS_SAFEGUARD_STOP in robot_dashboard.get_safety_status():
                messagebox.showerror("Kann nicht starten", "Der Roboter ist in einem Sicherheitsstop. Sind die Türen geschlossen und wurde der Reset-Taster gedrückt?")
                return 
            
            loaded_images.clear()
            start_command()
            start_button.config(state=tk.DISABLED)
        except Exception as exception:
            log.error("Exception in start_command: ", exc_info=exception)
            messagebox.showerror("Ein Fehler ist aufgetreten", exception)

    def quit():
        msg_box = tk.messagebox.askquestion('Programm beenden', 'Wirklich beenden?\n\n (Zum Neustarten auf "Prüfstand" auf dem Desktop doppel klicken.)', icon='warning')
        if msg_box == 'yes':
            root.destroy()

    start_button = tk.Button(frame, font=font, text=f"Start",
                            bg="gray", width=2, height=1, command=start_pressed)
    start_button.grid(row=1, column=1, padx=5, pady=5, sticky='nsew')

    quit_button = tk.Button(frame, font=font, text=f"Beenden",
                            bg=COLORS["warnung"], width=2, height=1, command=quit)
    quit_button.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')

    for x in range(3):
        frame.grid_columnconfigure(x, weight=1)
    for y in range(3):
        frame.grid_rowconfigure(y, weight=1)

    for x in range(8):
        root.grid_columnconfigure(x, weight=1)
    for y in range(5):
        root.grid_rowconfigure(y, weight=1)

    def process_message(message):
        if message is not None:
            add_line_to_log_output(message)
            update_overview_tool_buttons()
        else:
            start_button.config(state=tk.NORMAL)
            messagebox.showwarning("Achtung", "Der Prüflauf wurde beendet. \n\nVor dem nächsten Start muss sich der Roboter in der Home-Position befinden. \n\nHierzu kann bei Bedarf PolyScope genutzt werden.")

    def after_callback():
        try:
            # read all messages in queue until empty exception
            while True:
                message = thread_queue.get(block=False)
                process_message(message)
        except queue.Empty:
            root.after(100, after_callback)

    root.after(100, after_callback)

    # root = tk.Tk()
    root.bind('<Escape>', lambda event: root.destroy())
    root.mainloop()

