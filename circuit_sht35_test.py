import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice

'''
- 2022/02/08 ver.0.02
- Author : emguse
- License: MIT License
'''

I2C_ADRESS=0x45 # 0x44 (default)

def CRC(data):
    crc = 0xFF
    for s in data:
        crc ^= s
        for i in range(8):
            if crc & 0x80:
                crc <<= 1
                crc ^= 0x31
            else:
                crc <<= 1
    crc = crc & 0xFF
    return crc

class TemperatureHumiditySensorSHT35():
    def __init__(self, i2c) -> None:
        self.device = I2CDevice(i2c, I2C_ADRESS)
    def read_order(self) -> None:
        with self.device:
            start_order = bytes([0x24, 0x00])
            raw = bytearray(6)
            self.device.write_then_readinto(start_order, raw)
        # read 6 bytes back
        # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        temperature = raw[0] * 256 + raw[1]
        celsius = -45 + (175 * temperature / 65535.0)
        humidity = 100 * (raw[3] * 256 + raw[4]) / 65535.0
        if raw[2] != CRC(raw[:2]):
            print(raw[2])
            raise RuntimeError("temperature CRC mismatch")
        if raw[5] != CRC(raw[3:5]):
            raise RuntimeError("humidity CRC mismatch")
        return celsius, humidity


def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    sht35 = TemperatureHumiditySensorSHT35(i2c)
    while True:
        temperature, humidity = sht35.read_order()
        print('Temperature: {:.2f} C'.format(temperature))
        print('Humidity: {:.2f} %'.format(humidity))
        time.sleep(1)

if __name__ == "__main__":
  main()
