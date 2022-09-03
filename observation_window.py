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
        pos_entry = []
        for _ in range(10):
            strvar = tkinter.StringVar()
            self.pos_strvar.append(strvar)
            pos_entry.append(tkinter.Entry(self.frame2, textvariable=strvar, state="readonly", width=3))
        pos_entry[0].grid(row = 0, column = 0)

        pos_entry[1].grid(row = 1, column = 0)
        pos_entry[2].grid(row = 1, column = 1)
        pos_entry[3].grid(row = 1, column = 2)
        pos_entry[4].grid(row = 2, column = 0)
        pos_entry[5].grid(row = 2, column = 2)
        pos_entry[6].grid(row = 3, column = 0)
        pos_entry[7].grid(row = 3, column = 1)
        pos_entry[8].grid(row = 3, column = 2)

        pos_entry[9].grid(row = 2, column = 1)

        self.event.set()

        self.window.after(1000, self._check_to_quit)
        self.window.mainloop()

        # need to delete variables that reference tkinter objects in the thread
        del self.value

        for _ in range(10):
            del self.pos_strvar[0]

        del self.frame1
        del self.frame2
        del self.window

    def _check_to_quit(self):
        if self.running:
            self.window.after(1000, self._check_to_quit)
        else:
            self.window.destroy()

    def quit(self):
        self.running = False


def test():
    obswin = ObservationWindow()
    thread = threading.Thread(target=obswin.start)
    thread.start()

    obswin.event.wait(2)
    
    for i in range(10):
        obswin.pos_strvar[i].set(i)

    for i in 1, 2, 3:
        obswin.value.set(i)
        time.sleep(0.5)

    obswin.quit()
    thread.join()

if __name__ == '__main__':
    test()