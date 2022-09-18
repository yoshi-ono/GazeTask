import time
import threading
import tkinter

class ObservationWindow:
    def __init__(self):
        self.event = threading.Event()
        self.event.clear()

    def start(self):
        self.running = True
        self.window = tkinter.Tk()
        self.window.title("OBSERVATION")
        self.window.geometry('320x520')

        # フレーム１
        self.frame1 = tkinter.Frame(self.window)
        self.frame1.pack(pady=20)

        self.label_status = tkinter.Label(self.frame1,
                                text="STATUS",
                                font=("", 20, "bold"))
        self.label_status.pack()

        #self.label = tkinter.Label(self.frame1, text="Reward:", relief="sunken", bg="red", width=10)
        self.label = tkinter.Label(self.frame1,
                                text="Reward:",
                                font=("", 20, "bold"))
        self.label.pack()

        self.value = tkinter.StringVar()
        self.entry = tkinter.Entry(self.frame1,
                                textvariable=self.value,
                                state="readonly",
                                width=5,
                                font=("", 20, "bold"),
                                justify="center")
        self.entry.pack()

        # フレーム２
        self.frame2 = tkinter.Frame(self.window)
        self.frame2.pack(pady=20)

        self.pos_strvar = []
        self.pos_entry = []
        for _ in range(10):
            strvar = tkinter.StringVar()
            self.pos_strvar.append(strvar)
            entry = tkinter.Entry(self.frame2,
                                textvariable=strvar,
                                width=3,
                                font=("", 20, "bold"),
                                justify="center")
            self.pos_entry.append(entry)

        self.pos_entry[0].grid(row = 0, column = 0)

        self.pos_entry[1].grid(row = 1, column = 0)
        self.pos_entry[2].grid(row = 1, column = 1)
        self.pos_entry[3].grid(row = 1, column = 2)
        self.pos_entry[4].grid(row = 2, column = 0)
        self.pos_entry[5].grid(row = 2, column = 2)
        self.pos_entry[6].grid(row = 3, column = 0)
        self.pos_entry[7].grid(row = 3, column = 1)
        self.pos_entry[8].grid(row = 3, column = 2)

        self.pos_entry[9].grid(row = 2, column = 1)

        # フレーム ワーキングメモリ
        self.frame_wm = tkinter.Frame(self.window)
        self.frame_wm.pack(pady=20)

        self.wm_strvar = []
        self.wm_entry = []
        for _ in range(10):
            strvar = tkinter.StringVar()
            self.wm_strvar.append(strvar)
            entry = tkinter.Entry(self.frame_wm,
                                textvariable=strvar,
                                width=3,
                                font=("", 20, "bold"),
                                justify="center")
            self.wm_entry.append(entry)

        self.wm_entry[0].grid(row = 0, column = 0)

        self.wm_entry[1].grid(row = 1, column = 0)
        self.wm_entry[2].grid(row = 1, column = 1)
        self.wm_entry[3].grid(row = 1, column = 2)
        self.wm_entry[4].grid(row = 2, column = 0)
        self.wm_entry[5].grid(row = 2, column = 2)
        self.wm_entry[6].grid(row = 3, column = 0)
        self.wm_entry[7].grid(row = 3, column = 1)
        self.wm_entry[8].grid(row = 3, column = 2)

        self.wm_entry[9].grid(row = 2, column = 1)

        self.event.set()

        self.window.after(1000, self._check_to_quit)
        self.window.mainloop()

        # need to delete variables that reference tkinter objects in the thread
        del self.label
        del self.value
        del self.entry

        for _ in range(10):
            del self.pos_strvar[0]
            del self.pos_entry[0]
            del self.wm_strvar[0]
            del self.wm_entry[0]

        del self.frame1
        del self.frame2
        del self.frame_wm
        del self.window

    def _check_to_quit(self):
        if self.running:
            self.window.after(1000, self._check_to_quit)
        else:
            # self.frame1.destroy()
            # self.frame2.destroy()
            self.window.destroy()

    def quit(self):
        self.running = False

    def set_pos_color(self, pos):
        for i in range(10):
            self.pos_entry[i]["bg"] = "white"
        
        self.pos_entry[pos]["bg"] = "red"


def test():
    obswin = ObservationWindow()
    thread = threading.Thread(target=obswin.start)
    thread.start()

    obswin.event.wait(2)
    
    for i in range(10):
        obswin.pos_strvar[i].set(i)

    for i in 1, 2, 3:
        obswin.value.set(i)
        obswin.pos_entry[i]["bg"] = "red"
        time.sleep(0.5)

    obswin.label["bg"] = "yellow"
    obswin.label["text"] = "黄色"
    time.sleep(1)

    obswin.quit()
    thread.join()

if __name__ == '__main__':
    test()