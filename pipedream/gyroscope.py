import serial
import threading
import struct

class GyroscopeHandler:
    def __init__(self, port='/dev/ttyUSB0', baud=9600, dataCallback=None):
        self.serial = serial.Serial(port, baud, timeout=100)
        self.dataCallback = dataCallback
        self.buffer = bytearray()
        self.running = True
         
        self.values = {
            0x51: [0.0,0.0,0.0],
            0x52: [0.0,0.0,0.0],
            0x53: [0.0,0.0,0.0],
        }
        self.zeroValues = {
            0x51: [0.0,0.0,0.0],
            0x52: [0.0,0.0,0.0],
            0x53: [0.0,0.0,0.0],
        }
        
    def start(self):
        thread = threading.Thread(target=self.read_serial_loop, daemon=True)
        thread.start()

    def convert_hex(self, packet):
        if len(packet) != 11 or packet[0] != 0x55:
            return None

        dtype = packet[1]
        payload = packet[2:10]
        checksum = packet[10]
        if (sum(packet[:10]) & 0xFF) != checksum:
            return None  # Checksum mismatch

        # Convert payload to signed shorts
        vals = struct.unpack('<hhh', payload[0:6])
        scale = {
            0x51: 16.0 * 9.8 / 32768.0,  # Acceleration
            0x52: 2000.0 / 32768.0,      # Angular velocity
            0x53: 180.0 / 32768.0        # Angle
        }

        if dtype in scale:
            return dtype, [v * scale[dtype] for v in vals]
        else:
            return None  # Unknown data type
    
    def zero(self, state):
        if state == 1:
            self.zeroValues = {k: list(v) for k, v in self.values.items()}
        elif state == 0:
            self.zeroValues = {
                0x51: [0.0,0.0,0.0],
                0x52: [0.0,0.0,0.0],
                0x53: [0.0,0.0,0.0],
            }
        return

    def read_serial_loop(self):
        while self.running:
            data = self.serial.read(33) # 1 packet = 33 bytes
            self.buffer.extend(data)

            while len(self.buffer) >= 11:
                if self.buffer[0] == 0x55:
                    packet = self.buffer[:11]
                    parsed = self.convert_hex(packet)
        
                    if parsed:
                        dtype, value = parsed
                        self.values[dtype] = value
                        
                        adjustedValues = [v - z for v,z in zip(self.values[dtype], self.zeroValues[dtype])]
                    
                        if self.dataCallback:
                            self.dataCallback(dtype, adjustedValues)  # Trigger callback to gui
                        
                    self.buffer = self.buffer[11:]
                else:
                    self.buffer.pop(0) # Misaligned, drop byte
    
    def stop(self):
        self.running = False
        self.serial.close()
