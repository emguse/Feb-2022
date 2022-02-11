import board
import busio
import time
from adafruit_dps310.advanced import DPS310_Advanced as DPS310

'''
- 2022/02/10 ver.0.01
- Author : emguse
- License: MIT License
'''

SEA_LEVEL_PRESSURE = 1013.25

class BarometricPressureSensorDPS310():
    def __init__(self, i2c) -> None:
        self.dps310 = DPS310(i2c)
    def altitude_calc(self, c, p):
        return ((SEA_LEVEL_PRESSURE/p)**(1/5.257)-1)*(c+273.15)/0.0065
    def temperature(self):
        celsius = self.dps310.temperature
        return celsius
    def pressure(self):
        pressure = self.dps310.pressure
        return pressure
    def read(self):
        celsius = self.dps310.temperature
        pressure = self.dps310.pressure
        altitude = self.altitude_calc(celsius, pressure)
        return celsius, pressure, altitude

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    dps310 = BarometricPressureSensorDPS310(i2c)
    while True:
        temperature, pressure, altitude = dps310.read()
        print(temperature, pressure, altitude)
        print('Temperature: {:.2f} C'.format(temperature))
        print('Pressure   : {:.2f} hPa'.format(pressure))
        print('Altitude   : {:.2f} m'.format(altitude))
        time.sleep(1)

if __name__ == "__main__":
    main()
