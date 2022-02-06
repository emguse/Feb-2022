import board
import time
import busio
from adafruit_dps310.basic import DPS310


def main():
    i2c = busio.I2C()
    dps310 = DPS310(i2c)

    while True:
        print("Tmp = %.2f *C" % dps310.temperature)
        print("Prs = %.2f hPa" % dps310.pressure)
        print("")
        time.sleep(1.0)
    
if __name__ == "__main__":
  main()