from tkinter.ttk import *

def style_button():
    style = Style()

    btn_style = 'W.TButton'
    style.configure(btn_style, font =
               ('calibri', 10, 'bold'),
                background = 'pale turquoise')

    return btn_style

def style_frame():
    style = Style()

    frame_style = 'W.TFrame'
    style.configure(frame_style, background = 'pale turquoise')

    return frame_style
