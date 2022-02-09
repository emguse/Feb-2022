import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice

'''
- 2022/02/09 ver.0.03
- Author : emguse
- License: MIT License
'''

I2C_ADRESS=0x45 # 0x44 (default)
PERIODIC = False

class TemperatureHumiditySensorSHT35():
    def __init__(self, i2c) -> None:
        self.device = I2CDevice(i2c, I2C_ADRESS)
    def _CRC(self, data):
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
    def _conversion(self, raw):
        temperature = raw[0] * 256 + raw[1]
        celsius = -45 + (175 * temperature / 65535.0)
        humidity = 100 * (raw[3] * 256 + raw[4]) / 65535.0
        if raw[2] != self._CRC(raw[:2]):
            print(raw[2])
            raise RuntimeError("temperature CRC mismatch")
        if raw[5] != self._CRC(raw[3:5]):
            raise RuntimeError("humidity CRC mismatch")
        return celsius,humidity
    def read_order(self):
        with self.device:
            start_order = bytes([0x24, 0x00])
            raw = bytearray(6)
            self.device.write_then_readinto(start_order, raw)
            # read 6 bytes back
            # Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        celsius, humidity = self._conversion(raw)
        return celsius, humidity
    def periodic_order(self):
        with self.device:
            periodic_order = bytes([0x27, 0x37])
            self.device.write(periodic_order)
    def read_periodic(self):
        with self.device:
            start_order = bytes([0xE0, 0x00])
            self.device.write(start_order)
            time.sleep(0.001)
            raw = bytearray(6)
            self.device.readinto(raw)
        celsius, humidity = self._conversion(raw)
        return celsius, humidity

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    sht35 = TemperatureHumiditySensorSHT35(i2c)
    past_tk = 0
    if PERIODIC:
        sht35.periodic_order()
        time.sleep(1)
    while True:
        now = time.monotonic()
        if PERIODIC:
            if past_tk + 1/10 <= now: 
                temperature, humidity =sht35.read_periodic()
            past_tk = time.monotonic()
        else:
            temperature, humidity = sht35.read_order()
            time.sleep(1)
        print('Temperature: {:.2f} C'.format(temperature))
        print('Humidity: {:.2f} %'.format(humidity))
        #time.sleep(1)

if __name__ == "__main__":
    main()
