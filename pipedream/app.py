import tkinter as tk
from .camera import CameraFeed
from .controller import ControllerHandler
from .gyroscope import GyroscopeHandler

class Application:
    def __init__(self, root, useCamera, useGyro, useController):
        # Enable Modules
        self.useCamera = useCamera
        self.useGyro = useGyro
        self.useController = useController
        
        # Create GUI
        self.root = root
        self.root.title("Pipedream Satellite GUI")
        
        # Camera
        if self.useCamera:
            # Video Label
            self.videoLabel = tk.Label(self.root, text="Live Fishing Camera Feed")
            self.videoLabel.grid(row=0, column=1, padx=5, pady=5)

            # Taken Image
            self.imageLabel = tk.Label(self.root, text="Taken Image")
            self.imageLabel.grid(row=1, column=1, padx=5, pady=5)
            
            # Camera Handler
            self.camera = CameraFeed()
            self.update_video()

        # Controller
        if self.useController:
            # Controller Command Table
            self.create_command_table()

            # Controller Handler
            self.controller = ControllerHandler(
                shutdownCallback=self.safe_shutdown,
                captureCallback=self.capture_image,
                commandCallback=self.highlight_command,
                zeroGyroCallback=self.zero_gyro
            )
            self.controller.start()

        # Gyroscope
        if self.useGyro:
            # Gyroscope Table
            self.create_gyro_table()
        
            # Gyroscope Handler
            self.gyro = GyroscopeHandler(
                dataCallback=self.update_gyro_labels,                
            )
            self.gyro.start()

        # Clean Exit
        self.root.protocol("wmDeleteWINDOW", self.safe_shutdown)

    def create_command_table(self):
        self.commandFrame = tk.Frame(self.root, borderwidth=2, relief="groove", padx=5, pady=5)
        self.commandFrame.grid(row=0, column=0, padx=5, pady=5, sticky="n")

        commands = [
            ("Capture Image", "Back"),
            ("Quit", "Start"),
            ("Pitch Up", "LT"),
            ("Pitch Down", "RT"),
            ("Roll Left", "LB"),
            ("Roll Right", "RB"),
            ("Ascend", "A"),
            ("Descend", "B"),
            ("Zero Gyro", "X"),
            ("Remove Zero", "Y"),
            ("Forward Translation", "Left Stick Up"),
            ("Backwards Translation", "Left Stick Down"),
            ("Left Translation", "Left Stick Left"),
            ("Right Translation", "Left Stick Right"),
            ("Left Yaw", "Right Stick Left"),
            ("Right Yaw", "Right Stick Right")
        ]
        
        self.commandLabels = {} 

        # Table Headers
        tk.Label(self.commandFrame, text="Command", font=("Helvetica", 10, "bold")).grid(row=0, column=1, sticky="w", padx=5)
        tk.Label(self.commandFrame, text="Button", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5)

        # Table Rows
        for i, (command, button) in enumerate(commands, start=1):
            commandLabel = tk.Label(self.commandFrame, text=command)
            commandLabel.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            
            buttonLabel = tk.Label(self.commandFrame, text=button)
            buttonLabel.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            self.commandLabels[command] = (commandLabel, buttonLabel)

    def highlight_command(self, commandName, state):
        labels = self.commandLabels.get(commandName)
        if labels:
            commandLabel, buttonLabel = labels
            
            if state == 1:
                commandLabel.config(bg="red", fg="white")
                buttonLabel.config(bg="red", fg="white")
            else:
                self.reset_label_color(commandLabel, buttonLabel)

    def reset_label_color(self, commandLabel, buttonLabel):
            commandLabel.config(bg=self.commandFrame["bg"], fg="black")
            buttonLabel.config(bg=self.commandFrame["bg"], fg="black")

    def create_gyro_table(self):
        self.mainGyroFrame = tk.Frame(self.root, borderwidth=2, relief="groove", width=320, height=480)
        self.mainGyroFrame.grid(row=1, column=0, padx=5, pady=5, sticky="n")

        # Inner frames for each data category
        self.accFrame = tk.Frame(self.mainGyroFrame, borderwidth=1, relief="groove", width=150, height=100)
        self.accFrame.grid(row=0, column=0, padx=5, pady=5)
        self.accFrame.grid_propagate(False)
        
        self.gyroFrame = tk.Frame(self.mainGyroFrame, borderwidth=1, relief="groove", width=150, height=100)
        self.gyroFrame.grid(row=1, column=0, padx=5, pady=5)
        self.gyroFrame.grid_propagate(False)

        self.angleFrame = tk.Frame(self.mainGyroFrame, borderwidth=1, relief="groove", width=150, height=100)
        self.angleFrame.grid(row=2, column=0, padx=5, pady=5)
        self.angleFrame.grid_propagate(False)
        
        # Container for dynamic updates from gyroscope handler
        self.gyroLabels = {}
        
        # Create gyroscope unit labels
        self.gyroUnits = {
                "ax": "m/s^2", "ay": "m/s^2", "az": "m/s^2",
                "gx": "deg/s", "gy": "deg/s", "gz": "deg/s",
                "pitch": "deg", "roll": "deg", "yaw": "deg" 
        }
        
        # Populate data sections
        self.populate_gyro_section(self.accFrame, "Acceleration", ["ax", "ay", "az"])
        self.populate_gyro_section(self.gyroFrame, "Angular Velocity", ["gx", "gy", "gz"])
        self.populate_gyro_section(self.angleFrame, "Angle", ["pitch", "roll", "yaw"])

    def populate_gyro_section(self, frame, title, labels): 
        # Header
        tk.Label(frame, text=title, font=("Helvetica", 10, "bold")).grid(row=0, column=0, columnspan=2, padx=5, pady=2)

        # Table Rows
        for i, (label) in enumerate(labels, start=1):
            tk.Label(frame, text=label+":").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            
            unit = self.gyroUnits.get(label, "")
            
            valueLabel = tk.Label(frame, text=f"0.00 {unit}")
            valueLabel.grid(row=i, column=1, sticky="e", padx=5, pady=2)
            
            self.gyroLabels[label] = valueLabel
    
    def update_gyro_labels(self, dtype, values):
        if dtype == 0x51: # Acceleration
                keys = ["ax", "ay", "az"]
        elif dtype == 0x52: # Angular Velocity
                keys = ["gx", "gy", "gz"]
        elif dtype == 0x53: # Angle
                keys = ["pitch", "roll", "yaw"]
        else:
                return
        
        for key, value in zip(keys, values):
                if key in self.gyroLabels:
                        unit = self.gyroUnits.get(key, "")
                        self.gyroLabels[key].config(text=f"{value:.2f} {unit}")
                        
    def zero_gyro(self, state):
            self.gyro.zero(state)
                        
    def update_video(self):
        self.camera.update_label(self.videoLabel)
        self.root.after(30, self.update_video)

    def capture_image(self):
        self.camera.update_label(self.imageLabel)
        self.camera.save_image()
    
    def safe_shutdown(self):
        self.root.after(0, self.on_close)
        
    def on_close(self):
        if self.useCamera:
            self.camera.release()
        if self.useGyro:
            self.gyro.stop()
        self.root.quit()
        self.root.destroy()
