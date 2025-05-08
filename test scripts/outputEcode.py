import evdev

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if device.name == "Logitech Gamepad F310":
        controller = device
if controller == None:    
    raise Exception("Controller not found")

for event in controller.read_loop():
    print(evdev.categorize(event))
    
    if event.code == evdev.ecodes.ABS_Z:
        print("ZZZ")
