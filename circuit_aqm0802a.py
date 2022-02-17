import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice

print("Hello World!")

'''
- 2022/02/17 ver.0.02
- Author : emguse
'''

I2C_ADRESS=0x3e
SET_IS_0 = bytes([0x00, 0x38])
SET_IS_1 = bytes([0x00, 0x39])
IOSC_FREQ = bytes([0x00, 0x14])
INITIAL_CONT = 0x20
FOLLOWER_CTL = bytes([0x00, 0x6C])
CLEAR_DISP = bytes([0x00, 0x01])
ENTRY_MODE = bytes([0x00, 0x07])

class CharacterLcdAqm0802():
    def __init__(self, i2c) -> None:
        self.device = I2CDevice(i2c, I2C_ADRESS)
        self.disp_on = True
        self.cursor_on = True
        self.cur_blink_on = True

        self.set_is_0()
        time.sleep(0.0000263)
        self.set_is_1()
        time.sleep(0.0000263)
        self.set_iosc_freq()
        time.sleep(0.0000263)
        self.set_contrast(INITIAL_CONT)
        time.sleep(0.0000263)
        self.set_folower()
        time.sleep(0.2)
        self.set_is_0()
        time.sleep(0.0000263)
        self.set_display_onoff()
        time.sleep(0.0000263)
        self.clear_disp()
        time.sleep(0.108)
    def set_is_0(self):
        with self.device:
            self.device.write(SET_IS_0)
    def set_is_1(self):
        with self.device:
            self.device.write(SET_IS_1)
    def set_iosc_freq(self):
        with self.device:
            self.device.write(IOSC_FREQ)
    def set_contrast(self, cont):
        c1234 = cont & 0b00001111
        contrast_set = 0b01110000 | c1234
        c56 = (cont & 0b00110000) >> 4
        pw_icon_cont = 0b01010100 | c56
        with self.device:
            self.device.write(bytes([0x00, contrast_set]))
            time.sleep(0.0000263)
            self.device.write(bytes([0x00, pw_icon_cont]))
    def set_folower(self):
        with self.device:
            self.device.write(FOLLOWER_CTL)
    def set_display_onoff(self):
        cmd = 0b00001111
        if self.disp_on == False:
            cmd = cmd & 0b11111011
        if self.cursor_on == False:
            cmd = cmd & 0b11111101
        if self.cur_blink_on == False:
            cmd = cmd & 0b11111110
        with self.device:
            self.device.write(bytes([0x00, cmd]))
    def clear_disp(self):
        with self.device:
            self.device.write(CLEAR_DISP)
    def entry_mode(self):
        with self.device:
            self.device.write(ENTRY_MODE)
    def send_chr(self, s):
        self.cut_8(s)
        with self.device:
            for c in s:
                self.device.write(bytes([0x40, ord(c)]))
    def cut_8(self, s):
        s = s[:8]
        return s

def main():
    i2c = busio.I2C(board.GP3, board.GP2)
    lcd = CharacterLcdAqm0802(i2c)
    while True:
        print('Input string')
        s = input()
        if len(s) > 8:
            s = lcd.cut_8(s)
        lcd.clear_disp()
        lcd.send_chr(str(s))

if __name__ == "__main__":
    main()