import struct
import time

from serial import Serial

from src.utils.helper import check_received_angles, clear_input_buffer

ser = Serial(
    port="/dev/ttyACM1",
    baudrate=9600,
    timeout=0.1,
)


print("++++++++++++++++++++++ Done connection! ++++++++++++++++++++++++++++")
clear_input_buffer(ser)
status = ""

i = 0
while status != "done":
    data = ser.read_until().decode().strip()
    print(data)
    # size_bytes = ser.read(4)
    # if len(size_bytes) < 4:
    #     print("Error: Failed to read the size of the array.")

    # size = struct.unpack('I', size_bytes)[0]
    # print("Received array size:", size)

    # # Read the array data from Arduino
    # data_bytes = ser.read(size * 4)
    # if len(data_bytes) < size * 4:
    #     print("Error: Failed to read the complete array data.")

    # float_array = struct.unpack('f' * size, data_bytes)

    # print(float_array)
