import evdev 
import gpiozero
import time
import threading
        
def normalize_joystick(value):
    return 2 * (value + 32768) / (32767 + 32768) - 1
 
deadzone = 0.2 
 
thruster_groups = {
    "A": [
        gpiozero.OutputDevice(3),
        gpiozero.OutputDevice(4),
        gpiozero.OutputDevice(27),
        gpiozero.OutputDevice(21),
        gpiozero.OutputDevice(13),
        gpiozero.OutputDevice(26)
    ],
    "B": [
        gpiozero.OutputDevice(23), 
        gpiozero.OutputDevice(22), 
        gpiozero.OutputDevice(12),
        gpiozero.OutputDevice(20), 
        gpiozero.OutputDevice(19),
        gpiozero.OutputDevice(2)
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
        gpiozero.OutputDevice(8)
    ]
}
    
class ControllerHandler:
    def __init__(self, on_shutdown_callback=None, on_capture_callback=None, on_command_callback=None, on_zero_gyro_callback=None):
        if on_shutdown_callback:
            self.on_shutdown = on_shutdown_callback
        if on_capture_callback:
            self.on_capture = on_capture_callback
        if on_command_callback:
            self.on_command = on_command_callback
        if on_zero_gyro_callback:
            self.on_zero_gyro = on_zero_gyro_callback
        
        self.commands = {
            "fTrans":  [thruster_groups["C"][0], thruster_groups["C"][3], thruster_groups["D"][0], thruster_groups["D"][3]],
            "bTrans":  [thruster_groups["A"][0], thruster_groups["A"][3], thruster_groups["B"][0], thruster_groups["B"][3]],
            "lTrans":  [thruster_groups["A"][4], thruster_groups["B"][4], thruster_groups["C"][4], thruster_groups["D"][4]],
            "rTrans":  [thruster_groups["A"][1], thruster_groups["B"][1], thruster_groups["C"][1], thruster_groups["D"][1]],
            "ascend":  [thruster_groups["B"][2], thruster_groups["B"][5], thruster_groups["D"][2], thruster_groups["D"][5]],
            "descend": [thruster_groups["A"][2], thruster_groups["A"][5], thruster_groups["C"][2], thruster_groups["C"][5]],
            "lYaw":    [thruster_groups["A"][2], thruster_groups["B"][5], thruster_groups["C"][2], thruster_groups["D"][5]],
            "rYaw":    [thruster_groups["A"][5], thruster_groups["B"][2], thruster_groups["C"][5], thruster_groups["D"][2]],
            "uPitch":  [thruster_groups["A"][2], thruster_groups["A"][5], thruster_groups["D"][2], thruster_groups["D"][5]],
            "dPitch":  [thruster_groups["B"][2], thruster_groups["B"][5], thruster_groups["C"][2], thruster_groups["C"][5]],
            "lRoll":   [thruster_groups["A"][4], thruster_groups["B"][4], thruster_groups["C"][1], thruster_groups["D"][1]],
            "rRoll":   [thruster_groups["A"][1], thruster_groups["B"][1], thruster_groups["C"][4], thruster_groups["D"][4]],
#            "dock":    [],
        }
        
        self.active_left_command = None
        self.active_right_command = None
        
        self.controller = self.find_controller()
        
        self.left_x =  0
        self.left_y =  0
        self.right_x = 0
        self.right_y = 0
        
    def find_controller(self):
        for device in [evdev.InputDevice(path) for path in evdev.list_devices()]:
            if device.name == "Logitech Gamepad F310":
                return device
        raise Exception("Controller not found")
        
    def start(self):
        thread = threading.Thread(target=self.controller_loop)
        thread.start()
        
    def controller_loop(self):
        for event in self.controller.read_loop():
            # Start Button
            if event.code == 315:
                if self.on_command:
                    self.on_command("Quit", 1)
                    
                if self.on_shutdown:
                    self.on_shutdown()
                return
                
            # Back Button
            if event.code == 314:
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Capture Image", 1)
                                
                    if self.on_capture:
                        self.on_capture()
                else:
                    if self.on_command:
                        self.on_command("Capture Image", 0)
                
            # Left Joystick
            if event.code in [evdev.ecodes.ABS_X, evdev.ecodes.ABS_Y]:
                if event.code == evdev.ecodes.ABS_X:
                    self.left_x = normalize_joystick(event.value)
                    if self.left_x < -deadzone:
                        print("Left")
                    elif self.left_x > deadzone:
                        print("Right")
                elif event.code == evdev.ecodes.ABS_Y:
                    self.left_y = normalize_joystick(event.value)
                    if self.left_y < -deadzone:
                        print("Up")
                    elif self.left_y > deadzone:
                        print("Down")
                    
                for direction in ["lTrans", "rTrans", "fTrans", "bTrans"]:
                    for device in self.commands[direction]:
                        device.off()
                
                new_command = None
                # SOMETHING WRONG WITH THE DEADZONE NORMALIZATION CODE (?)

                if self.left_x < -deadzone:
                    new_command = "Left Translation"
                    for device in self.commands["lTrans"]:
                        device.on()
                elif self.left_x > deadzone:
                    new_command = "Right Translation"
                    for device in self.commands["rTrans"]:
                        device.on()

                if self.left_y < -deadzone:
                    new_command = "Forward Translation"     
                    for device in self.commands["fTrans"]:
                        device.on()
                elif self.left_y > deadzone:
                    new_command = "Backwards Translation"
                    for device in self.commands["bTrans"]:
                        device.on()

                if new_command != self.active_left_command:
                    if self.active_left_command and self.on_command:
                        self.on_command(self.active_left_command, 0)
                    if new_command and self.on_command:
                        self.on_command(new_command, 1)
                    self.active_left_command = new_command

            # Right Joystick
            elif event.code in [evdev.ecodes.ABS_RX, evdev.ecodes.ABS_RY]:
                if event.code == evdev.ecodes.ABS_RX:
                    self.right_x = normalize_joystick(event.value)
                elif event.code == evdev.ecodes.ABS_RY:
                    self.right_y = normalize_joystick(event.value)

                for direction in ["lYaw", "rYaw"]:
                    for device in self.commands[direction]:
                        device.off()

                new_command = None

                if self.right_x < -deadzone:
                    new_command = "Left Yaw"
                    for device in self.commands["lYaw"]:
                         device.on()
                elif self.right_x > deadzone:
                    new_command = "Right Yaw"
                    for device in self.commands["rYaw"]:
                        device.on()
                
                if new_command != self.active_right_command:
                    if self.active_right_command and self.on_command:
                        self.on_command(self.active_right_command, 0)
                    if new_command and self.on_command:
                        self.on_command(new_command, 1)
                    self.active_right_command = new_command

            # Triggers
            if event.code == 2: # L
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Pitch Down", 1)
                            
                    for device in self.commands["dPitch"]:
                        device.on()
                else:
                    if self.on_command:
                        self.on_command("Pitch Down", 0)
                            
                    for device in self.commands["dPitch"]:
                        device.off()
            if event.code == 5: # R
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Pitch Up", 1)
                            
                    for device in self.commands["uPitch"]:
                        device.on()
                else:
                    if self.on_command:
                        self.on_command("Pitch Up", 0)
                            
                    for device in self.commands["uPitch"]:
                        device.off()
                   
            # Buttons 
            if event.code == 304: # A
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Ascend", 1)
                            
                    for device in self.commands["ascend"]:
                        device.on()
                else:
                    if self.on_command:
                        self.on_command("Ascend", 0)
                            
                    for device in self.commands["ascend"]:
                        device.off()
            if event.code == 305: # B
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Descend", 1)
                            
                    for device in self.commands["descend"]:
                        device.on()
                else:
                    if self.on_command:
                        self.on_command("Descend", 0)
                            
                    for device in self.commands["descend"]:
                        device.off()
            if event.code == 307: # X
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Zero Gyro", 1)
                    
                    if self.on_zero_gyro:
                        self.on_zero_gyro(1)
                else:
                     if self.on_command:
                        self.on_command("Zero Gyro", 0)
            if event.code == 308: # Y
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Reset Gyro", 1)
                    
                    if self.on_zero_gyro:
                        self.on_zero_gyro(0)
                else:
                    if self.on_command:
                        self.on_command("Reset Gyro", 0)
            if event.code == 310: # LB
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Roll Left", 1)
                            
                    for device in self.commands["lRoll"]:
                        device.on()
                else:
                    if self.on_command:
                        self.on_command("Roll Left", 0)
                        
                    for device in self.commands["lRoll"]:
                        device.off()
            if event.code == 311: # RB
                if event.value > 0:
                    if self.on_command:
                        self.on_command("Roll Right", 1)
                            
                    for device in self.commands["rRoll"]:
                        device.on()
                else:
                    if self.on_command:
                        self.on_command("Roll Right", 0)
                            
                    for device in self.commands["rRoll"]:
                        device.off()
