from tkinter.ttk import *

def style_button():
    style = Style()

    btn_style = 'W.TButton'
    style.configure(btn_style, font =
               ('calibri', 10, 'bold'),
                relief='flat', background='thistle4', activebackground='thistle4')

    return btn_style

def style_frame():
    style = Style()

    frame_style = 'W.TFrame'
    style.configure(frame_style, background = 'antique white')

    return frame_style

def root_style(master):
    style = Style(master)
    style.theme_use('clam')
