import cv2
import datetime
from PIL import Image, ImageTk

class CameraFeed:
    def __init__(self, cameraIndex=0):
        self.cap = cv2.VideoCapture(cameraIndex)
        if not self.cap.isOpened():
            raise Exception("Camera not found")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2image)

    def get_imageTk_frame(self):
        image = self.get_frame()
        if image:
            return ImageTk.PhotoImage(image)
        return None

    def update_label(self,label):
        imgtk = self.get_imageTk_frame()
        if imgtk:
            label.imgtk = imgtk
            label.config(image=imgtk)

    def save_image(self):
        ret, frame = self.cap.read()

        if ret:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filepath = f"./images/image_{timestamp}.jpg"

            cv2.imwrite(filepath, frame)

    def release(self):
        self.cap.release()
