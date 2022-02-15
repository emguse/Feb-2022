import board
import busio
import time

AT = "AT"
AT_MODE = "AT+CWMODE?"
AT_CWMODE1 = "AT+CWMODE=1"
AT_CWLAP = "AT+CWLAP"
AT_CWJAP = "AT+CWJAP="
AT_CHK_IF = "AT+CIFSR"
AT_CWQAP = "AT+CWQAP"

path = './secret.txt'

INTERVAL = 5.0
TIMEOUT = 30.0

uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0)

last_time = 0
message = []
send_command = False

with open(path) as f:
    lines = []
    for line in f:
        s = ""
        for c in line:
            if c == "\r":
                break
            else:
                s += c
        lines.append(s)
    SSID = "\"" + str(lines[0]) + "\"" 
    PASSWORD = "\"" + str(lines[1]) + "\"" 

def at():
    uart.write(bytes(f"{AT}\r\n", "ascii"))
def at_chk_mode():
    uart.write(bytes(f"{AT_MODE}\r\n", "ascii"))
def at_set_cwmode_1():
    uart.write(bytes(f"{AT_CWMODE1}\r\n", "ascii"))
def at_list_ap():
    uart.write(bytes(f"{AT_CWLAP}\r\n", "ascii"))
def at_join_ap():
    uart.write(bytes(f"{AT_CWJAP}{SSID},{PASSWORD}\r\n", "ascii"))
def at_quit_ap():
    uart.write(bytes(f"{AT_CWQAP}\r\n", "ascii"))
def at_show_ip():
    uart.write(bytes(f"{AT_CHK_IF}\r\n", "ascii"))

while True:
    now = time.monotonic()
    if  send_command == False:
        val = ""
        val = input()
        if val == "at":
            at()
        elif val == "mode":
            at_chk_mode()
        elif val == "set1":
            at_set_cwmode_1()
        elif val == "list":
            at_list_ap()
        elif val == "join":
            at_join_ap()
        elif val == "quit":
            at_quit_ap()
        elif val == "show":
            at_show_ip()
        else:
            continue
        send_command = True
        now = time.monotonic()
        last_time = now
    if send_command == True:
        if now >= last_time + TIMEOUT:
            print("command time out")
            send_command = False

    byte_read = uart.read(1)
    if byte_read is None:
        continue
    else:
        message_started = True
    if message_started:
        if byte_read == b"\r":
            message_started = False
            msg = ""
            for s in message:
                msg += s
            print(msg)
            #print(bytearray(msg))
            if msg == "\nOK":
                print("command complete")
                send_command = False
            if msg == "\nFAIL":
                print("command incomplete")
                end_command = False
            message = []
            continue
        else:
            message.append(chr(byte_read[0]))
