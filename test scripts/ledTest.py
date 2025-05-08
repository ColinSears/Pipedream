## Import Statements
import gpiozero
import time

led = LED(17)

led.on()
time.sleep(2)
led.off()