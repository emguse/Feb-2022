import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice

print("Hello World!")

'''
- 2022/02/18 ver.0.03
- Author : emguse
'''

_I2C_ADRESS=0x3e
_FOLLOWER_CTL = 0x6C

_CLEAR_DISP = 0x01
_RETURN_HOME = 0x02

_ENTRY_MODE_SET = 0x04

_DISP_ON_OFF = 0x08
_SET_CGRAM = 0x40
_SET_DDRAM = 0x80

_FUNCTION_SET = 0x20 # const
_BIT_MODE_8 = 0x10 # const
_NUM_OF_LINE_2 = 0x08 # const

_IOSC_FREQ = 0x10
_BIAS = 0x04
_ADJ_IOSC_FREQ = 0x00

_INITIAL_CONT = 0x20

class CharacterLcdAqm0802():
    def __init__(self, i2c) -> None:
        self.device = I2CDevice(i2c, _I2C_ADRESS)
        self.disp_on = True
        self.cursor_on = True
        self.cur_blink_on = True
        self.direction = 1
        self.shift_entry = 0
        self.screen_cursor_select = 0
        
        self.instruction_table = 0
        self.init_display()
    def init_display(self):
        self.instruction_table = 0
        self._function_set(self.instruction_table, _BIT_MODE_8, _NUM_OF_LINE_2)
        time.sleep(0.0000263)
        self.instruction_table = 1
        self._function_set(self.instruction_table, _BIT_MODE_8, _NUM_OF_LINE_2)
        time.sleep(0.0000263)
        self._set_iosc_freq()
        time.sleep(0.0000263)
        self._set_contrast(_INITIAL_CONT)
        time.sleep(0.0000263)
        self._set_folower()
        time.sleep(0.2)
        self.instruction_table = 0
        self._function_set(self.instruction_table, _BIT_MODE_8, _NUM_OF_LINE_2)
        time.sleep(0.0000263)
        self._set_display_onoff()
        time.sleep(0.0000263)
        self.clear_disp()
        time.sleep(0.108)
    def _send_cmmand(self, com):
        with self.device:
            self.device.write(bytes([0x00, com]))
    def send_chr(self, s):
        self.cut_8(s)
        with self.device:
            for c in s:
                self.device.write(bytes([0x40, ord(c)]))
    def cut_8(self, s):
        s = s[:8]
        return s
    def _function_set(self, is_, bit, line):
        self._send_cmmand(_FUNCTION_SET | is_ | bit | line)
    def _set_iosc_freq(self):
        self._send_cmmand(_IOSC_FREQ | _BIAS | _ADJ_IOSC_FREQ)
    def _set_contrast(self, cont):
        c1234 = cont & 0b00001111
        contrast_set = 0b01110000 | c1234
        c56 = (cont & 0b00110000) >> 4
        pw_icon_cont = 0b01010100 | c56
        self._send_cmmand(contrast_set)
        time.sleep(0.0000263)
        self._send_cmmand(pw_icon_cont)
    def _set_folower(self):
        self._send_cmmand(_FOLLOWER_CTL)
    def _set_display_onoff(self):
        cmd = 0b00001111
        if self.disp_on == False:
            cmd = cmd & 0b11111011
        if self.cursor_on == False:
            cmd = cmd & 0b11111101
        if self.cur_blink_on == False:
            cmd = cmd & 0b11111110
        self._send_cmmand(cmd)
    def clear_disp(self):
        self._send_cmmand(_CLEAR_DISP)
    def return_home(self):
        self._send_cmmand(_RETURN_HOME)
    def _entry_mode(self):
        self._send_cmmand(_ENTRY_MODE_SET | (self.direction << 1) | self.shift_entry)
    def _shift_mode(self):
        self._send_cmmand()
    def set_direction_left_to_right(self):
        self.direction = 1
        self._entry_mode()
    def set_direction_right_to_left(self):
        self.direction = 0
        self._entry_mode()
    def set_string_shift_left(self):
        self.shift_entry = 1
        self._entry_mode()
    def set_string_shift_never(self):
        self.shift_entry = 0
        self._entry_mode()

def main():
    i2c = busio.I2C(board.GP3, board.GP2)
    lcd = CharacterLcdAqm0802(i2c)
    while True:
        print('Input string')
        s = input()
        #print(bytearray(s))
        #print(s == '@direction to left')
        if s == '@cls':
            lcd.clear_disp()
            continue
        elif s == '@init display':
            lcd.init_display()
            lcd.set_direction_left_to_right()
            lcd.set_string_shift_left()
            lcd.return_home
            continue
        elif s == '@direction to right':
            lcd.set_direction_left_to_right()
            continue
        elif s == '@direction to left':
            lcd.set_direction_right_to_left()
            continue
        elif s == '@string shift never':
            lcd.set_string_shift_never()
            continue
        elif s == '@string shift left':
            lcd.set_string_shift_left()
            continue
        #lcd.clear_disp()
        if len(s) > 8:
            s = lcd.cut_8(s)
        lcd.send_chr(str(s))

if __name__ == "__main__":
    main()