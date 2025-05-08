import tkinter as tk
from pipedream import Application

def main():
    root = tk.Tk()
    app = Application(root, useCamera=1, useGyro=1, useController=1)
    root.mainloop()

if __name__ == "__main__":
    main()
