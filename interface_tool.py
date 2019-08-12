from tkinter import Tk
import multiprocessing
from dashboard_frame import *
from parse2 import *
from pcfg_grammar import *
from sentence import *
from tkinter.ttk import Progressbar
from time import sleep
from nltk.treeprettyprinter import TreePrettyPrinter
from nltk import Tree

class App:
    def __init__(self, master):

        self.root = master
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit)
        self.set_app_title(master, "Parsing Tool")
        self.status = {
            'parsing': False
        }

        self.main_frame = ATIHorizontalGrid(master, expand=True, relief="sunken")
        self.gr_frame = ATIHorizontalGrid(master, expand=True, relief="sunken")

        self.input_frame = ATIDashboard(self.main_frame.frame, expand=True)
        self.input_label = ATILabel(self.input_frame.frame, text='Input Goes Here')
        self.output_frame = ATIDashboard(self.main_frame.frame, expand=True)
        self.output_label = ATILabel(self.output_frame.frame, text='Output Appears Here')
        self.menu_frame = ATIDashboard(self.main_frame.frame, relief="sunken")

        self.log = ATILog(self.input_frame.frame, scrollbar=True)
        self.output_log = ATILog(self.output_frame.frame, scrollbar=True)
        self.output_log.log.config(state="disabled")

        self.parse_button = ATIButton(self.menu_frame.frame, text="Parse", btn_response=self.parse_btn_response)

        self.progressbar = Progressbar(mode="determinate", orient="horizontal", length=200)

        self.gr_label = ATILabel(self.gr_frame.frame, text='PCFG Grammar Rules')
        self.gr_log = ATILog(self.gr_frame.frame, scrollbar=True)

        self.gr = PCFG_Grammar('./test.gr')

        for nt in self.gr.get_non_terminals():
            for rule in self.gr.get_rules(nt):
                self.gr_log.add_text(rule.get_rule_str(), align='left')


    def set_app_title(self, master, title):
        top_level = master.winfo_toplevel()
        top_level.title(title)

    def parse_btn_response(self):
        if not self.status['parsing']:
            self.parse()
        else:
            self.process.terminate()

    def parse(self):

        self.status['parsing'] = True
        self.parse_button.button.config(text="Stop")

        self.output_log.clear(disable = True)

        sen = Sentence(self.log.retrieve_text())

        self.recv_end, send_end = multiprocessing.Pipe(False)
        self.process = multiprocessing.Process(target=parse_sen, args=(self.gr, sen, send_end, True))

        self.progressbar.pack()
        self.log.log.config(state="disabled")
        self.root.config(cursor="wait")
        self.root.update()

        self.process.start()
        self.progressbar.start()
        self.root.after(50, self.check_completed)

    def check_completed(self):
        if self.process.is_alive():
            self.root.after(50, self.check_completed)
        else:
            self.status['parsing'] = False
            self.parse_button.button.config(text="Parse")

            self.progressbar.stop()
            self.progressbar.pack_forget()
            self.log.log.config(state="normal")
            try:
                output_str = self.recv_end.recv()
            except EOFError:
                output_str = ''

            if not output_str == '' and output_str is not None:
                self.output_log.add_text(TreePrettyPrinter(Tree.fromstring(output_str)), disable=True)

            self.root.config(cursor="")
            self.root.update()

    def ask_quit(self):
        self.root.destroy()
        self.root.quit()

root = Tk()
root.minsize(width=500, height=400)

root_style(root)
app = App(root)

root.mainloop()
