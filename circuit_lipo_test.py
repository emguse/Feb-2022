import board
import busio
import time
import neopixel
from rainbowio import colorwheel
from adafruit_lc709203f import LC709203F

print("Hello World!")

class OnbordNeopix():
    def __init__(self) -> None:
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=False)
        self.pixel.brightness = 0.1
        self.color_step = 0

    def rainbow(self, delay):
        for color_value in range(255):
            for led in range(1):
                pixel_index = (led * 256 // 1) + color_value
                self.pixel[led] = colorwheel(pixel_index & 255)
            self.pixel.show()
            time.sleep(delay)

    def rainbow_step(self): # Each time it is called, it advances the color one step
        self.color_step += 1
        self.pixel[0] = colorwheel(self.color_step & 255)
        self.pixel.show()

class LipoStatLC709203F():
    '''
    ic_version - Read-only chip version
    cell_voltage - Floating point voltage
    cell_percent - Percentage of cell capacity
    power_mode - Current power mode (operating or sleeping)
    pack_size - current battery pack size
    '''
    def __init__(self, i2c) -> None:
        self.lipo_stat = LC709203F(i2c)
    def version(self):
        return self.lipo_stat.ic_version # Read-only chip version
    def voltage(self):
        return self.lipo_stat.cell_voltage # Floating point voltage
    def percent(self):
        return self.lipo_stat.cell_percent # Percentage of cell capacity
    def mode(self):
        return self.lipo_stat.power_mode # Current power mode (operating or sleeping)
    def size(self):
        return self.lipo_stat.pack_size # current battery pack size

def main():
    onbord_neopix = OnbordNeopix()
    i2c = busio.I2C(board.SCL, board.SDA)
    
    lipo = LipoStatLC709203F(i2c)
    print("version:", hex(lipo.version()))

    past_time_onbord_neopix = 0
    past_time_lipo_stat = 0

    while True:
        t = time.monotonic()
        
        if t - past_time_onbord_neopix >= 0.01:
            onbord_neopix.rainbow_step()
            past_time_onbord_neopix = time.monotonic()
        
        if t - past_time_lipo_stat >= 10:
            print("Bat_volt: %0.3f V" % (lipo.voltage()))
            print("Bat_volt: %0.3f V" % (lipo.voltage()))
            print("Bat_Pct: %0.1f %%" % (lipo.percent()))
            print("Bat_mode: ", lipo.mode())
            past_time_lipo_stat = time.monotonic()

if __name__ == '__main__':
    main()