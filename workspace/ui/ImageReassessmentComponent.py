from ui.ScrollableImage import ScrollableImage
from helper.tool_assessment import ToolAssessment, ToolState, NUMBER_OF_PICTURES
import tkinter as tk
from ui.Common import load_and_resize_image, COLORS, root, font

loaded_images = []


ICON_PATH = './assets/images'
ICON_SCALE = 0.03
ICON_GOOD = load_and_resize_image(f"{ICON_PATH}/good.png", ICON_SCALE, ICON_SCALE)
ICON_BAD = load_and_resize_image(f"{ICON_PATH}/bad.png", ICON_SCALE, ICON_SCALE)
ICON_RECYCLE = load_and_resize_image(f"{ICON_PATH}/recycle.png", ICON_SCALE, ICON_SCALE)

loaded_images.append(ICON_GOOD)
loaded_images.append(ICON_BAD)
loaded_images.append(ICON_RECYCLE)


def create_image_reassessment_component(parent, image_path, row_pos, col_pos, tool: ToolAssessment, image_number, tool_number, update_parent):
    current_image = image_number
    img_obj = load_and_resize_image(image_path, scale_x=0.35, scale_y=0.35)
    loaded_images.append(img_obj)

    main_frame = tk.Frame(parent, border=1, relief="solid", bg="lightgray")
    main_frame.grid(row=row_pos, column=col_pos, padx=5, pady=5, sticky='nsew')

    def open_zoom():
        current_zoom_image = current_image
        
        def load_image():
            img_zoom = tk.PhotoImage(file=tool.get_image_paths(current_zoom_image)["image_path_high_resolution"])
            loaded_images.append(img_zoom)
            return img_zoom
 

        modal = tk.Toplevel(root)
        modal.overrideredirect(True)
        modal.geometry(
            "{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

        def change_image(offset):
            nonlocal current_zoom_image, ai_assessment
            current_zoom_image = (current_zoom_image + offset) % NUMBER_OF_PICTURES
            image_window.set_image(load_image())
            update_frame_text()
            ai_assessment = tool.get_ai_assessment(current_zoom_image)
            update_button_colors()

        

        def update_frame_text():
            nonlocal top_frame_label
            top_frame_label.config(text=f"Werkzeug {tool_number} Bild {current_zoom_image+1}")

        top_frame = tk.Frame(modal)
        top_frame_label = tk.Label(top_frame, font=font)
        update_frame_text()
        top_frame_label.pack(side='left', padx='50')

        back_button = tk.Button(top_frame, text="zurück", height=1, command=lambda: modal.destroy(), font=font,
                                relief="solid")
        back_button.pack(side='right', padx= 10)
        top_frame.pack(fill='x')
        
        ai_assessment = tool.get_ai_assessment(current_zoom_image)

        # ufff
        button_frame = tk.Frame(top_frame)
        def update_button_colors():
            state = tool.get_state(current_zoom_image)
            button1_color = COLORS["gut"] if state == ToolState.GOOD else "white"
            button1.config(bg=button1_color, highlightbackground=button1_color)
            button2_color = COLORS["schlecht"] if state == ToolState.BAD else "white"
            button2.config(bg=button2_color, highlightbackground=button2_color)
            button3_color = COLORS["neutral"] if state == ToolState.RECYCLE else "white"
            button3.config(bg=button3_color, highlightbackground=button3_color)

        def select_button(state):
            tool.set_operator_assessment(current_zoom_image, state)
            update_parent()
            update_button_colors()

        def create_button(text, state, icon):
            button = tk.Button(button_frame, text=text,
                            command=lambda: select_button(state), image=icon, compound="left", height=60, width=210,
                            relief="solid", border=1, font=("Helvetica", 11, "bold"))
            return button

        button1_text = "Gut\n (KI)" if ai_assessment == ToolState.GOOD else "Gut"
        button1 = create_button(button1_text, ToolState.GOOD, ICON_GOOD)

        button2_text = "Schlecht\n (KI)" if ai_assessment == ToolState.BAD else "Schlecht"
        button2 = create_button(button2_text, ToolState.BAD, ICON_BAD)

        button3_text = "Aufbereiten\n (KI)" if ai_assessment == ToolState.RECYCLE else "Aufbereiten"
        button3 = create_button(button3_text, ToolState.RECYCLE, ICON_RECYCLE)
        button3.pack(side='right', padx= 10)
        button2.pack(side='right')
        button1.pack(side='right', padx= 10)
        button_frame.pack(padx=10, pady=10)
        update_button_colors()
        # uffff
        
        next_button = tk.Button(modal, text=">", width=4, height=40, font=font, relief="groove", command=lambda offset=1 :change_image(offset))
        next_button.pack(side='right') # , fill='y'
        previous_button = tk.Button(modal, text="<", width=4, height=40, font=font, relief="groove", command=lambda offset=-1 :change_image(offset))
        previous_button.pack(side='left') # , fill='y'

        image_window = ScrollableImage(modal, image=load_image(), scrollbarwidth=24,
                                       width=root.winfo_screenwidth(), height=root.winfo_screenheight() - 50)
        image_window.pack()

        # zoomed_image_button = tk.Button(modal, image=img_zoom, command=lambda: modal.destroy())
        # zoomed_image_button.pack()

    label = tk.Button(main_frame, image=img_obj, command=lambda: open_zoom())
    label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

    ai_assessment = tool.get_ai_assessment(current_image)

    def update_button_colors():
        state = tool.get_state(current_image)
        button1_color = COLORS["gut"] if state == ToolState.GOOD else "white"
        button1.config(bg=button1_color, highlightbackground=button1_color)
        button2_color = COLORS["schlecht"] if state == ToolState.BAD else "white"
        button2.config(bg=button2_color, highlightbackground=button2_color)
        button3_color = COLORS["neutral"] if state == ToolState.RECYCLE else "white"
        button3.config(bg=button3_color, highlightbackground=button3_color)

    def select_button(state):
        tool.set_operator_assessment(current_image, state)
        update_button_colors()

    def create_button(text, state, icon, column):
        button = tk.Button(main_frame, text=text,
                           command=lambda: select_button(state), image=icon, compound="left", height=50, width=110,
                           relief="solid", border=1, font=("Helvetica", 11, "bold"))
        button.grid(row=1, column=column, padx=5, pady=5, sticky='nsew')
        return button

    button1_text = "Gut\n (KI)" if ai_assessment == ToolState.GOOD else "Gut"
    button1 = create_button(button1_text, ToolState.GOOD, ICON_GOOD, 0)

    button2_text = "Schlecht\n (KI)" if ai_assessment == ToolState.BAD else "Schlecht"
    button2 = create_button(button2_text, ToolState.BAD, ICON_BAD, 1)

    button3_text = "Aufbereiten\n (KI)" if ai_assessment == ToolState.RECYCLE else "Aufbereiten"
    button3 = create_button(button3_text, ToolState.RECYCLE, ICON_RECYCLE, 2)

    update_button_colors()

    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_rowconfigure(1, weight=2)
    # main_frame.grid_rowconfigure(2, weight=1)

    return update_button_colors
