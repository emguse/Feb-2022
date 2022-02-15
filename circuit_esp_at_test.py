import board
import busio
import time

INTERVAL = 3.0

uart = busio.UART(board.GP0, board.GP1, baudrate=115200, timeout=0)

last_time = 0

AT = "AT"

while True:
    now = time.monotonic()
    if  now - last_time >= INTERVAL:
        print("send: " + AT)
        uart.write(bytes(f"{AT}\r\n", "ascii"))
        last_time = now
    time.sleep(0.1)
    data = uart.read(256)
    if data is not None:
        print("receive")
        data_string = ''.join([chr(b) for b in data])
        print(data_string, end="")
        print("")
