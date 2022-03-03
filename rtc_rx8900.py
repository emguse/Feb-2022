import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice

'''
- 2022/03/03 ver.0.05
- Author : emguse
'''

_I2C_ADRESS=0x32
_TSTA_1S = 1.0 # Ta=25degC:1sec 
_TSTA_3S = 3.0 # Ta=-40to85degC:3sec

_MIN_ALM_REG = 0x08
_HOUR_ALM_REG = 0x09
_W_D_ALM_REG = 0x0A
_SEC_REG = 0x10
_MIN_REG = 0x11
_HOUR_REG = 0x12
_WEEK_REG = 0x13
_DAY_REG = 0x14
_MONTH_REG = 0x15
_YEAR_REG = 0x16
_TEMP_REG = 0x17
_BUCK_UP_FUNC_REG = 0x18
_TIMER_COUNTER_REG_0 = 0x1B
_TIMER_COUNTER_REG_1 = 0x1C
_EXTENSION_REG = 0x1D
_FLAG_REG = 0x1E
_CTRL_REG = 0x1F

DEFAULT_TIME = (2000, 1, 1, 0, 0, 0, 5, 0, 0)
TIME_ADJUST = True

class RealTimeClockRX8900():
    def __init__(self, i2c) -> None:
        self._device = I2CDevice(i2c, _I2C_ADRESS)
        self.ext_reg = {'WADA': 0, 'USEL': 0, 'TE': 0, 'FSEL': 0, 'TSEL': 0}
        self.flg_reg = {'UF': 0, 'TF': 0, 'AF': 0, 'VLF': 0, 'VDET': 0}
        self.ctl_reg = {'CSEL': 0, 'UIE': 0, 'TIE': 0, 'AIE': 0, 'RESET': 0}
        # Oscillation start time wait 
        time.sleep(_TSTA_1S)
        # Check VLF Bit
        self._read_flag_register()
        if self.flg_reg.get('VLF'):
            print("Detects supply voltage drop")
            print("All settings, including the time, will be reset")
            # Oscillation start time wait 
            time.sleep(_TSTA_1S)
            # Set Extension Register 0x0D,0x1D
            ext_reg_set = self._build_extension_register(False, False, False, 0x02, 0x02)
            self._write(_EXTENSION_REG, ext_reg_set)
            # Set Flag Register 0x0E,0x1E
            flg_reg_set = self._build_flag_register(False, False, False, False, False)
            self._write(_FLAG_REG, flg_reg_set)
            # Set Control Register 0X0F,0x1F
            ctl_reg_set = self._build_control_Register(0x01, False, False, False, True)
            self._write(_CTRL_REG, ctl_reg_set)
            # Current time setting
            self.time_adjust(*DEFAULT_TIME)
    def _write(self, addr, data):
        write_data = []
        write_data.append(addr)
        write_data.extend(data)
        #print(write_data)
        with self._device:
            self._device.write(bytes(write_data))
    def _read(self, length):
        bytes_read = bytearray(length)
        with self._device:
            self._device.readinto(bytes_read)
        return bytes_read
    def _read_from_addr(self, addr, length):
        bytes_read = bytearray(length)
        with self._device:
            self._device.write_then_readinto(bytes([addr]), bytes_read)
        return bytes_read
    def _build_extension_register(self, wada, usel, te, fsel, tsel):
        '''
        Extension Register 0x0D,0x1D
        - WADA(Week Alarm /Day Alarm)
            - 0 : Week Alarm (Default when power is turned on)
            - 1  : Day Alarm
        - USEL(Update Interrupt Select)
            - 0 : Minutes update (Automatic recovery time : 7.813ms) (Default when power is turned on)
            - 1  : Second update (Automatic recovery time : 500ms)
        - TE(Timer Enable)
            - 0 : Stops the periodic timer interrupt function (Default when power is turned on)
            - 1 : Periodic timer interrupt function is activated
        - FSEL(FOUT Output frequency select)
            - 0 : 32.768 kHz (Default when power is turned on)
            - 1 : 1024 Hz
            - 2 : 1 Hz
            - 3 : 32.768 kHz
        - TSEL(Select countdown cycle (source clock))
            - 0 : 4096 Hz / 244.14 us / tRTN : 122 us
            - 1 : 64 Hz / 15.625 ms / tRTN : 7.813 ms
            - 2 : 1 Hz / 1s / tRTN : 7.813 ms (Default when power is turned on)
            - 3 : 1/60 Hz / 1min / tRTN : 7.813 ms
        '''
        TEST_MASK = 0b01111111 # Test bit mask(bit 7 is Never make it to True)
        data = TEST_MASK & (wada << 6 & 0x40) | (usel << 5 & 0x20) | (te << 4 & 0x10) | (fsel << 2 & 0x0C) | (tsel & 0x03)
        return bytes(data)
    def _read_extension_register(self):
        '''Update ext_reg :dict '''
        reg = self._read_from_addr(_EXTENSION_REG, 1)
        self.ext_reg['WADA'] = (reg[0] & 0x40) >> 6
        self.ext_reg['USEL'] = (reg[0] & 0x20) >> 5
        self.ext_reg['TE'] = (reg[0] & 0x10) >> 4
        self.ext_reg['FSEL'] = (reg[0] & 0x0C) >> 2
        self.ext_reg['TSEL'] = (reg[0] & 0x03)
    def _build_flag_register(self, uf, tf, af, vlf, vdet):
        '''
        Flag Register 0x0E,0x1E
        - UF(Update Flag) (The default setting at power-on is `0`)
            - Detects time update interrupts and retains results.
            - If it was '1' when reading, a time update interrupt has occurred.
            - Write `0` to clear. Release "/INT `L` " output.
        - TF(Timer Flag) (The default setting at power-on is `0`)
            - Detects a fixed-period timer interrupt and retains the result.
            - If it was '1' when reading,  a fixed-period timer interrupt has occurred.
            - Write `0` to clear. Release "/INT `L` " output.
        - AF(Alarm Flag) (The default setting at power-on is `0`)
            - Detects Alarm interrupts and retains results.
            - If it was '1' when reading,  a Alarm interrupt has occurred.
            - Write `0` to clear. Release "/INT `L` " output.
        - VLF(Voltage Low Flag) (The default setting at power-on is `1`)
            - A drop in the power supply voltage of the oscillation circuit was detected.
            - If the VLF bit indicates `1`, the crystal oscillation may have stopped or the power may have been turned off.
            - It is necessary to initialize all register data.
            - Holds `1` until writing `0`
        - VDET(Voltage Detect Flag) (The default setting at power-on is `1`)
            - Detects a drop in power supply voltage and retains the voltage state detection result of the temperature compensation circuit.
            - Indicates that the temperature compensation operation may have stopped, that is, the reliability of the time data is slightly low.
            - Holds `1` until writing `0`
        '''
        data = (uf << 5 & 0x20) | (tf << 4 & 0x10) | (af << 3 & 0x08) | (vlf << 1 & 0x02) | (vdet % 0x01)
        return bytes(data)
    def _read_flag_register(self) -> None:
        '''Update flg_reg :dict '''
        reg = self._read_from_addr(_FLAG_REG, 1)
        self.flg_reg['UF'] = (reg[0] & 0x20) >> 5
        self.flg_reg['TF'] = (reg[0] & 0x10) >> 4
        self.flg_reg['AF'] = (reg[0] & 0x08) >> 3
        self.flg_reg['VLF'] = (reg[0] & 0x02) >> 1
        self.flg_reg['VDET'] = (reg[0] & 0x01)
    def _build_control_Register(self, csel, uie, tie, aie, reset):
        '''
        Control Register 0X0F,0x1F
        - CSEL(Compensation interval Select)
            - Set the temperature compensation interval
                - 0 : 0.5 s
                - 1 : 2.0 s (Default when power is turned on)
                - 2 : 10 s
                - 3 : 30 s
        - UIE(Update Interrupt Enable) (The default setting at power-on is `0`)
            - Specify whether to generate interrupt signal when an interrupt factor for time update occurs.
        - TIE(Timer Interrupt Enable) (The default setting at power-on is `0`)
            - Specify whether to generate interrupt signal when an interrupt factor for timer update occurs.
        - AIE(Alarm Interrupt Enable) (The default setting at power-on is `0`)
            - Specify whether to generate interrupt signal when an interrupt factor for Alarm update occurs.
        - RESET (The default setting at power-on is `0`)
            - Setting the bit to "1" will reset the counter to less than a second.
        '''
        data = (csel << 6 & 0xC0) | (uie << 5 & 0x20) | (tie << 4 & 0x10) | (aie << 3 & 0x08) | (reset & 0x01)
        return bytes(data)
    def _read_control_Register(self):
        '''Update ctl_reg :dict '''
        reg = self._read_from_addr(_CTRL_REG, 1)
        self.ctl_reg['CSEL'] = (reg[0] & 0xC0) >> 6
        self.ctl_reg['UIE'] = (reg[0] & 0x20) >> 5
        self.ctl_reg['TIE'] = (reg[0] & 0x10) >> 4
        self.ctl_reg['AIE'] = (reg[0] & 0x08) >> 3
        self.ctl_reg['RESET'] = (reg[0] & 0x01)
    def _read_single_bit(self, addr, num_bits):
        bitmask = 0x01 << num_bits
        reg = self._read_from_addr(addr, 1)
        bits = (reg & bitmask) >> num_bits
        return bits
    def _set_single_bit(self, addr, num_bits, value):
        '''
        It does not work properly with time-related registers, 
        only with extension, control, and flag registers. (Depending on whether BCD is encoded)
        
        num_bits: MSB 76543210 LSB'''
        evacuation = self._read_from_addr(addr, 1)
        bitmask = (~(0x01 << num_bits) & 0xFF) & evacuation[0]
        value_to_set = value << num_bits
        prepared_value = bitmask | value_to_set
        self._write(addr, (prepared_value,))
    def datetime(self):
        t = self._bcd_to_struct(self._read_from_addr(_SEC_REG, 7))
        return t
    def _bcd_to_struct(self, raw_bcd):
        '''
        When it receives a 7-byte array of date/time data obtained from the RX8900, 
        it converts it to a date/time structure after BCD conversion.

        The order of the BCD sequences is (SEC, MIN, HOUR, WEEK, DAY, MONTH, YEAR) 
        '''
        if len(raw_bcd) != 7:
            raise ValueError("There is an excess or deficiency in the given time data")
        int_array = self._bcd_decode(raw_bcd)
        return time.struct_time((
            int_array[12] * 10 + int_array[13] + 2000, 
            int_array[10] * 10 + int_array[11], 
            int_array[8] * 10 + int_array[9], 
            int_array[4] * 10 + int_array[5], 
            int_array[2] * 10 + int_array[3], 
            int_array[0] * 10 + int_array[1], 
            self._day_of_the_week(raw_bcd[3]), 
            -1, 
            -1
        ))
    def _bcd_decode(self, bcd):
        '''Converts a given BCD array to an int array separated by a character and returns it.'''
        a = []
        for s in bytes(bcd):
            a.append(s >> 4)
            a.append(s & 0x0F)
        return a
    def _day_of_the_week(self, wday):
        '''If Sunday is the LSB and Saturday gives a different bit for each MSB day, 
        it returns 0 for Monday and 6 for Sunday.'''
        if wday == 0x01:
            return 6
        elif wday == 0x02:
            return 0
        elif wday == 0x04:
            return 1
        elif wday == 0x08:
            return 2
        elif wday == 0x10:
            return 3
        elif wday == 0x20:
            return 4
        elif wday == 0x40:
            return 5
        else:
            raise ValueError("Given an incorrect day of the week")
    def time_set(self, st :time.struct_time):
        '''
        Receives struct_time, corrects the number and converts it to BCD.
        '''
        converted =  self._build_the_time_for_setting(st)
        self._read_control_Register()
        ctl_reg_set = self._build_control_Register(
            self.ctl_reg.get('CSEL'), 
            self.ctl_reg.get('UIE'), 
            self.ctl_reg.get('TIE'), 
            self.ctl_reg.get('AIE'), 
            True
        )
        #print(converted)
        self._write(_CTRL_REG, ctl_reg_set)
        self._write(_SEC_REG, converted)
    def _build_the_time_for_setting(self, st :time.struct_time):
        if isinstance(st, time.struct_time) != True:
            raise ValueError("Data that is not `time.struct_time` was given")
        year = self._two_digit_extraction([st.tm_year])
        bcd_array = self._bcd_encode([
            year[0], st.tm_mon, st.tm_mday, st.tm_hour, st.tm_min, st.tm_sec
        ])
        return (bcd_array[5], bcd_array[4], bcd_array[3], 
            self._build_the_day_of_the_week(st.tm_wday), 
            bcd_array[2], bcd_array[1], bcd_array[0]
        )
    def _build_the_day_of_the_week(self, wday):
        w = 0x01 << wday
        w = w >> 1
        return w
    def _two_digit_extraction(self, value :list):
        for u in range(len(value)):
            lengths = len(str(value[u]))
            if lengths > 2:
                s = str(value[u])
                t = s[lengths - 2]
                t += s[lengths - 1]
                value[u] = int(t)
        return value
    def _bcd_encode(self, value):
        a = []
        for s in bytes(value):
            str_s = str(s)
            digit = len(str_s)
            bcd = 0
            for d in range(digit):
                bcd += int(str_s[d-1]) << d * 4
            a.append(bcd)
        return a
    def read_temp(self):
        raw = self._read(1)
        return (raw[0] * 2 - 187.19) / 3.218
    def set_min_alm_enable(self):
        evacuation = self._read_from_addr(_MIN_ALM_REG, 1)
        data = evacuation | 0x80
        self._write(_MIN_ALM_REG, data)
    def set_min_alm_disable(self):
        evacuation = self._read_from_addr(_MIN_ALM_REG, 1)
        data = evacuation & 0x7F
        self._write(_MIN_ALM_REG, data)
    def set_alm_min(self, min):
        bcd =  self._bcd_encode([min])
        bitarray = self._read_from_addr(_MIN_ALM_REG, 1)
        evacuation = bitarray & 0x80
        data = evacuation | bcd
        self._write(_MIN_ALM_REG, data)
    def set_hour_alm_enable(self):
        evacuation = self._read_from_addr(_HOUR_ALM_REG, 1)
        data = evacuation | 0x80
        self._write(_MIN_ALM_REG, data)
    def set_hour_alm_disable(self):
        evacuation = self._read_from_addr(_HOUR_ALM_REG, 1)
        data = evacuation & 0x7F
        self._write(_MIN_ALM_REG, data)
    def set_alm_hour(self, hour):
        bcd =  self._bcd_encode([hour])
        bitarray = self._read_from_addr(_HOUR_ALM_REG, 1)
        evacuation = bitarray & 0x80
        data = evacuation | bcd
        self._write(_HOUR_ALM_REG, data)
    def set_alm_mode_week(self):
        bitarray = self._read_from_addr(_EXTENSION_REG, 1)
        data = bitarray & 0x7F
        self._write(_EXTENSION_REG, data)
    def set_alm_mode_day(self):
        bitarray = self._read_from_addr(_EXTENSION_REG, 1)
        data = bitarray | 0x80
        self._write(_EXTENSION_REG, data)
    def set_week_alm(self, week):
        if week == 6:
            week_bit = 0x01
        else:
            week_bit = 0x01 << (week + 1)
        bitarray = self._read_from_addr(_W_D_ALM_REG, 1)
        evacuation = bitarray & 0x80
        data = week_bit | evacuation
        self._write(_W_D_ALM_REG, data)
    def set_day_alm(self, day):
        bcd =  self._bcd_encode([day])
        bitarray = self._read_from_addr(_W_D_ALM_REG, 1)
        evacuation = bitarray & 0x80
        data = evacuation | bcd
        self._write(_W_D_ALM_REG, data)
    def set_timer_counter(self, timer):
        '''
        set counter
        0 to 4095 
        '''
        if timer < 4095:
            timer = 4095
            print("Timer out of range")
        tc0 = timer & 0x0FF
        tc1 = timer >> 8
        self._write(_TIMER_COUNTER_REG_0, tc0)
        self._write(_TIMER_COUNTER_REG_1, tc1)
    def set_timer_select(self, tsel):
        '''
        timer counter clock souce select
        - TSEL = 0: 4096 Hz
        - TSEL = 1: 64 Hz
        - TSEL = 2: 1 sec
        - TSEL = 3: 1 min
        '''
        self._read_extension_register()
        self.ext_reg['TSEL'] = tsel
        self._build_extension_register(
            self.ext_reg['WADA'], self.ext_reg['USEL'], self.ext_reg['TE'], 
            self.ext_reg['FSEL'], self.ext_reg['TSEL'])
    def set_timer_enable(self, te):
        '''
        - TE = 0: Timer Desable (Stop count down)
        - TE = 1: Timer Enable (Start count down)
        '''
        self._read_extension_register()
        self.ext_reg['TE'] = te
        ext_reg_set = self._build_extension_register(
            self.ext_reg['WADA'], self.ext_reg['USEL'], self.ext_reg['TE'], 
            self.ext_reg['FSEL'], self.ext_reg['TSEL'])
        self._write(_EXTENSION_REG, ext_reg_set)
    def set_timer_interrupt(self, tie):
        '''
        - TIE = 0: Desable timer interrupt
        - TIE = 1: Enable timer interrupt
        '''
        self._read_control_Register()
        self.ctl_reg['TIE'] = tie
        ctl_reg_set = self._build_control_Register(
            self.ext_reg['CSEL'], self.ext_reg['UIE'], self.ext_reg['TIE'], 
            self.ext_reg['AIE'], self.ext_reg['RESET'])
        self._write(_CTRL_REG, ctl_reg_set)
    def test(self):
        self.set_alm_min(59)


def main():
    i2c = busio.I2C(board.GP9, board.GP8)
    rtc = RealTimeClockRX8900(i2c)
    TIME_ADJUST = False
    if TIME_ADJUST:
        rtc.time_set(time.struct_time((2022, 2, 24, 22, 52, 0, 2, 0, 0)))
    while True:
        t = rtc.datetime()
        print('{:04}{:02}{:02}T{:02}{:02}{:02}'.format(
                t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min ,t.tm_sec))
        print(rtc.read_temp())
        #rtc.test()
        time.sleep(3)

if __name__ == "__main__":
    main()