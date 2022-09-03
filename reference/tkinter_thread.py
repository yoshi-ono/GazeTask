import time
import threading
import tkinter as tk


class GUI:

    def start(self):
        self.running = True
        self.window = tk.Tk()
        self.window.title("Sample")
        self.window.geometry('320x240')

        self.value = tk.StringVar()
        entry = tk.Entry(textvariable=self.value)
        entry.pack()

        self.window.after(1000, self._check_to_quit)
        self.window.mainloop()
        # need to delete variables that reference tkinter objects in the thread
        del self.value
        del self.window

    def _check_to_quit(self):
        if self.running:
            self.window.after(1000, self._check_to_quit)
        else:
            self.window.destroy()

    def quit(self):
        self.running = False


def main():
    gui = GUI()
    thread = threading.Thread(target=gui.start)
    thread.start()

    time.sleep(2)
    for i in 1, 2, 3, 'ダー!!':
        gui.value.set(i)
        time.sleep(1)

    gui.quit()
    thread.join()

if __name__ == '__main__':
    main()