import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import datetime
import imutils
#import evdev
#import serial

class Application():
    def __init__(self, root):
        self.root = root
        self.root.title("Pipedream Satellite GUI")

        # Figure out how to display controller inputs
        self.controller_label = tk.Label(self.root, text="Controller Input Placeholder")
        self.controller_label.grid(row=0, column=0, padx=5, pady=5)

        # Video Display
        self.video_label = tk.Label(self.root, text="Live Fishing Camera Feed")
        self.video_label.grid(row=0, column=1, padx=5, pady=5)
        
        # Need to figure out gyroscope data reading
        self.gyro_label = tk.Label(self.root, text="Gyroscope Readings Placeholder")
        self.gyro_label.grid(row=1, column=0, padx=5, pady=5)
           
        self.capture_frame = tk.Frame(self.root)
        self.capture_frame.grid(row=1, column=1, padx=5, pady=5)
        
        # Need to figure out how to make this button a controller input
        self.capture_button = tk.Button(self.capture_frame, text="Snap", command=self.captureImage)
        self.capture_button.pack()
        
        self.image_label = tk.Label(self.capture_frame, text="Taken Image Placeholder")
        self.image_label.pack()

        # Start Camera Display
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise Exception("Camera not found")
           
        self.updateVideo()
        
        # Start Gyroscope Reading
        
        # Start Controller Reading
        
        self.root.protocol("WM_DELTE_WINDOW", self.onClose)
    
    def updateVideo(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(img)
            
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)
            
        self.root.after(10, self.updateVideo)
        
    def captureImage(self):
        ret, frame = self.cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(img)
            
            self.image_label.imgtk = imgtk
            self.image_label.config(image=imgtk)
        
    def onClose(self):
        self.cap.release()
        self.root.destroy()
        
root = tk.Tk()    
app = Application(root)
root.mainloop()
