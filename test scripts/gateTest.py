import gpiozero
import time

#A 
#pins = [3, 4, 27, 21, 26, 13]
#B 
pins = [23, 22, 12, 20, 19, 2]
#C 
#pins = [7, 24, 25, 5, 6, 16]
#D 
#pins = [17, 18, 10, 9, 11, 8]
print(pins)
for pin in pins:
	device = gpiozero.OutputDevice(pin)
	print(pin)
	device.off()
	device.on()
	time.sleep(3)
	device.off()
