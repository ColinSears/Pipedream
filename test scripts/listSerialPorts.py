import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
print("Available Serial Ports:\n")

for i,port in enumerate(ports):
    print(f"[{i} {port.device} - {port.description}]")

if not ports:
    print("No serial ports found.")