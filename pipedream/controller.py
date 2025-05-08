import evdev
import gpiozero
import threading

# Identifier: [gpio(pins)]
PINOUT = {
    "A": [
        gpiozero.OutputDevice(3),
        gpiozero.OutputDevice(4),
        gpiozero.OutputDevice(27),
        gpiozero.OutputDevice(21),
        gpiozero.OutputDevice(26),
        gpiozero.OutputDevice(13)
        ],
    "B": [
        gpiozero.OutputDevice(23),
        gpiozero.OutputDevice(22), 
        gpiozero.OutputDevice(12),
        gpiozero.OutputDevice(20), 
        gpiozero.OutputDevice(19),
        gpiozero.OutputDevice(2),
        ],
    "C": [
        gpiozero.OutputDevice(7),
        gpiozero.OutputDevice(24),
        gpiozero.OutputDevice(25), 
        gpiozero.OutputDevice(5),  
        gpiozero.OutputDevice(6),
        gpiozero.OutputDevice(16)
        ],
    "D": [
        gpiozero.OutputDevice(17),
        gpiozero.OutputDevice(18),
        gpiozero.OutputDevice(10),
        gpiozero.OutputDevice(9),
        gpiozero.OutputDevice(11),
        gpiozero.OutputDevice(8),
        ]
}

# Command Label: PINOUT[Identifier][Index]
COMMANDS = {
    "Forward Translation": [
        PINOUT["C"][0], # C1
        PINOUT["C"][3], # C4
        PINOUT["D"][0], # D1
        PINOUT["D"][3]  # D4
        ],
    "Backwards Translation": [
        PINOUT["A"][0], # A1
        PINOUT["A"][3], # A4
        PINOUT["B"][0], # B1
        PINOUT["B"][3]  # B4
        ],
    "Left Translation": [
        PINOUT["A"][4], # A5
        PINOUT["B"][4], # B5
        PINOUT["C"][4], # C5
        PINOUT["D"][4]  # D5
        ],
    "Right Translation": [
        PINOUT["A"][1], # A2
        PINOUT["B"][1], # B2
        PINOUT["C"][1], # C2
        PINOUT["D"][1]  # D2
        ],
    "Ascend": [
        PINOUT["B"][2], # B3
        PINOUT["B"][5], # B6
        PINOUT["D"][2], # D3
        PINOUT["D"][5]  # D6
        ],
    "Descend": [
        PINOUT["A"][2], # A3
        PINOUT["A"][5], # A6
        PINOUT["C"][2], # C3
        PINOUT["C"][5]  # C6
        ],
    "Left Yaw": [
        PINOUT["A"][2], # A3
        PINOUT["B"][5], # B6
        PINOUT["C"][2], # C3
        PINOUT["D"][5]  # D6
        ],
    "Right Yaw": [
        PINOUT["A"][5], # A6
        PINOUT["B"][2], # B3
        PINOUT["C"][5], # C6
        PINOUT["D"][2]  # D3
        ],
    "Pitch Down": [
        PINOUT["A"][2], # A3
        PINOUT["A"][5], # A6
        PINOUT["D"][2], # D3
        PINOUT["D"][5]  # D6
        ],
    "Pitch Up": [
        PINOUT["B"][2], # B3
        PINOUT["B"][5], # B6
        PINOUT["C"][2], # C3
        PINOUT["C"][5]  # C6
        ],
    "Roll Left": [
        PINOUT["A"][4], # A5
        PINOUT["B"][4], # B5
        PINOUT["C"][1], # C2
        PINOUT["D"][1]  # D2
        ],
    "Roll Right":  [
        PINOUT["A"][1], # A2
        PINOUT["B"][1], # B2
        PINOUT["C"][4], # C5
        PINOUT["D"][4]  # D5
        ],
}

DEADZONE = 0.25

class ControllerHandler:
    def __init__(self, shutdownCallback=None, captureCallback=None, commandCallback=None, zeroGyroCallback=None):
        if shutdownCallback:
            self.shutdown = shutdownCallback
        if captureCallback:
            self.capture = captureCallback
        if commandCallback:
            self.commandInput = commandCallback
        if zeroGyroCallback:
            self.zeroGyro = zeroGyroCallback
        
        self.activeLCommand = None # Left Joystick Input
        self.activeRCommand = None # Right Joystick Input
        
        self.controller = self.find_controller()

    def find_controller(self):
        for device in [evdev.InputDevice(path) for path in evdev.list_devices()]:
            if device.name == "Logitech Gamepad F310":
                return device
        raise Exception("Controller not found")

    def start(self):
        thread = threading.Thread(target=self.controller_loop, daemon=True)
        thread.start()
    
    def read_button_input(self, value, command):
        if value > 0:
            if self.commandInput:
                self.commandInput(command, 1) # Highlight input
            
            # Handle buttons with callbacks
            if command == "Capture Image":
                if self.capture:
                    self.capture()
            if command == "Quit":
                if self.shutdown:
                    self.shutdown()
            if command == "Zero Gyro": 
                if self.zeroGyro:
                    self.zeroGyro(1)
            if command == "Reset Gyro":
                if self.zeroGyro:
                    self.zeroGyro(0)   
                    
            # Turn devices in COMMANDS list for given command on
            if command in COMMANDS:
                for device in COMMANDS[command]:
                    device.on()
        else:
            if self.commandInput:
                self.commandInput(command, 0) # Revert highlight
                
            # Turn devices in COMMANDS list for given command off
            if command in COMMANDS:
                for device in COMMANDS[command]:
                    device.off()
    
    def controller_loop(self):
        for event in self.controller.read_loop():
            # Handle Button Inputs
            if event.code == evdev.ecodes.BTN_SELECT:
                self.read_button_input(event.value, "Capture Image")
            if event.code == evdev.ecodes.BTN_START:
                self.read_button_input(event.value, "Quit")
            if event.code == evdev.ecodes.BTN_TL:
                self.read_button_input(event.value, "Roll Left")
            if event.code == evdev.ecodes.BTN_TR:
                self.read_button_input(event.value, "Roll Right")
            if event.code == evdev.ecodes.BTN_A:
                self.read_button_input(event.value, "Ascend")      
            if event.code == evdev.ecodes.BTN_B:
                self.read_button_input(event.value, "Descend")      
            if event.code == evdev.ecodes.BTN_X:
                self.read_button_input(event.value, "Zero Gyro")               
            if event.code == evdev.ecodes.BTN_Y:
                self.read_button_input(event.value, "Reset Gyro")   
            
             # Handle Trigger Inputs - Triggers can be read like buttons
            if event.code == evdev.ecodes.ABS_Z: # Left
                self.read_button_input(event.value, "Pitch Up")            
            if event.code == evdev.ecodes.ABS_RZ: # Right
                self.read_button_input(event.value, "Pitch Down")    
                        
            # Handle Joystick Inputs
            if event.type == evdev.ecodes.EV_ABS:
                if event.code in (evdev.ecodes.ABS_X, evdev.ecodes.ABS_Y): # Left Joystick         
                    currentLCommand = None
                    xLVal = 0
                    yLVal = 0
                    
                    if event.code == evdev.ecodes.ABS_X:
                        xLVal = event.value / 32768.0
                    elif event.code == evdev.ecodes.ABS_Y:
                        yLVal = event.value / 32768.0
                    
                    # Determine deadzone threshold to avoid small movements
                    if abs(xLVal) > DEADZONE or abs(yLVal) > DEADZONE:
                        if xLVal < -DEADZONE:
                            currentLCommand = "Left Translation"
                        elif xLVal > DEADZONE:
                            currentLCommand = "Right Translation"                        
                        if yLVal < -DEADZONE:
                            currentLCommand = "Forward Translation"
                        elif yLVal > DEADZONE:
                            currentLCommand = "Backwards Translation"
                            
                    if currentLCommand != self.activeLCommand:
                        if self.activeLCommand:
                            self.commandInput(self.activeLCommand, 0)
                            for device in COMMANDS[self.activeLCommand]:
                                device.off()
                        if currentLCommand:
                            self.commandInput(currentLCommand, 1)
                            for device in COMMANDS[currentLCommand]:
                                device.on()
                        self.activeLCommand = currentLCommand
                    
                if event.code in (evdev.ecodes.ABS_RX, evdev.ecodes.ABS_RY): # Right Joystick
                    currentRCommand = None
                    xRVal = 0
                    yRVal = 0
                    
                    if event.code == evdev.ecodes.ABS_RX:
                        xRVal = event.value / 32768.0
                    elif event.code == evdev.ecodes.ABS_RY:
                        yRVal = event.value / 32768.0
                    
                    # Determine deadzone threshold to avoid small movements
                    if abs(xRVal) > DEADZONE or abs(yRVal) > DEADZONE:
                        if xRVal < -DEADZONE:
                            currentRCommand = "Left Yaw"
                        elif xRVal > DEADZONE:
                            currentRCommand = "Right Yaw"                        
                        if yRVal < -DEADZONE:
                            currentRCommand = None
                        elif yRVal > DEADZONE:
                            currentRCommand = None
                                
                    if currentRCommand != self.activeRCommand:
                        if self.activeRCommand:
                            self.commandInput(self.activeRCommand, 0)
                            for device in COMMANDS[self.activeRCommand]:
                                device.off()
                        if currentRCommand:
                            self.commandInput(currentRCommand, 1)
                            for device in COMMANDS[currentRCommand]:
                                device.on()
                        self.activeRCommand = currentRCommand      
