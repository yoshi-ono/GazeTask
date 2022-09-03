import time
import threading
import tkinter


class StatusWindow:

    def start(self):
        self.running = True
        self.window = tkinter.Tk()
        self.window.title("STATUS")
        self.window.geometry('320x240')

        # フレーム１
        self.frame1 = tkinter.Frame(self.window)
        self.frame1.pack(pady=10)

        label = tkinter.Label(self.frame1, text="Reward:")
        label.pack()

        self.value = tkinter.StringVar()
        entry = tkinter.Entry(self.frame1, textvariable=self.value, state="readonly")
        entry.pack()


        # フレーム２
        self.frame2 = tkinter.Frame(self.window)
        self.frame2.pack(pady=10)

        self.pos_strvar = []
        self.pos_strvar.append(tkinter.StringVar())
        # pos_entry = []
        # for i in range(10):
        #     self.pos_strvar.append(tkinter.StringVar())
        #     pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos_strvar[i], state="readonly", width=3))
        self.pos0 = tkinter.StringVar()
        # self.pos1 = tkinter.StringVar()
        # self.pos2 = tkinter.StringVar()
        # self.pos3 = tkinter.StringVar()
        # self.pos4 = tkinter.StringVar()
        # self.pos5 = tkinter.StringVar()
        # self.pos6 = tkinter.StringVar()
        # self.pos7 = tkinter.StringVar()
        # self.pos8 = tkinter.StringVar()
        # self.pos9 = tkinter.StringVar()

        pos_entry = []
        pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos0, state="readonly", width=3))
        pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos_strvar[0], state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos2, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos3, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos4, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos5, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos6, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos7, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos8, state="readonly", width=3))
        # pos_entry.append(tkinter.Entry(self.frame2, textvariable=self.pos9, state="readonly", width=3))

        pos_entry[0].grid(row = 0, column = 0)

        pos_entry[1].grid(row = 1, column = 0)
        # pos_entry[2].grid(row = 1, column = 1)
        # pos_entry[3].grid(row = 1, column = 2)
        # pos_entry[4].grid(row = 2, column = 0)
        # pos_entry[5].grid(row = 2, column = 2)
        # pos_entry[6].grid(row = 3, column = 0)
        # pos_entry[7].grid(row = 3, column = 1)
        # pos_entry[8].grid(row = 3, column = 2)

        # pos_entry[9].grid(row = 2, column = 1)



        self.window.after(1000, self._check_to_quit)
        self.window.mainloop()
        # need to delete variables that reference tkinter objects in the thread
        del self.value

        # #for strvar in self.pos_strvar:
        # for i in range(10):
        #     del self.pos_strvar[i]
        del self.pos0
        del self.pos_strvar[0]

        del self.frame1
        del self.frame2
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


def test():
    gui = StatusWindow()
    thread = threading.Thread(target=gui.start)
    thread.start()

    time.sleep(2)
    
    # gui.pos0.set(0)
    # gui.pos1.set(0)
    # gui.pos2.set(0)
    # gui.pos3.set(0)
    # gui.pos4.set(0)
    # gui.pos5.set(0)
    # gui.pos6.set(0)
    # gui.pos7.set(0)
    # gui.pos8.set(0)
    # gui.pos9.set(0)

    for i in 1, 2, 3:
        gui.value.set(i)
        time.sleep(0.5)

    #time.sleep(10)
    gui.quit()
    time.sleep(2)
    thread.join()

if __name__ == '__main__':
    test()