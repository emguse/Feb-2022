import board
import busio
import time
from circuit_sht35 import TemperatureHumiditySensorSHT35 as SHT35
from circuit_dps310 import BarometricPressureSensorDPS310 as DPS310

'''
- 2022/02/11 ver.0.01
- Author : emguse
'''

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    dps310 = DPS310(i2c)
    sht35 = SHT35(i2c)
    while True:
        temperature, pressure, altitude = dps310.read()
        temperature_sht35, humidity = sht35.read_order() 
        print(temperature, humidity, pressure, altitude)
        print('Temperature: {:.2f} C'.format(temperature) + ' : {:.2f} C'.format(temperature_sht35))
        print('humidity   : {:.2f} %RH'.format(humidity))
        print('Pressure   : {:.2f} hPa'.format(pressure))
        print('Altitude   : {:.2f} m'.format(altitude))
        time.sleep(1)

if __name__ == "__main__":
    main()
