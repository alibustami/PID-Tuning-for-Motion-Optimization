import struct

from serial import Serial

object = Serial(
    port="/dev/ttyACM0",
    baudrate=9600,
    timeout=0.1,
)
# print("as;kjlasfd")
# kp = 1
# ki = 2
# kd = 3
# run_time = 5000
# dump_rate = 100
# values = f"{kp} {ki} {kd} {run_time} {dump_rate}\n"

# # while True:
# object.write(values.encode())
# if object.in_waiting > 0:
#     data_string = (
#         object.readline().decode("utf-8").strip()
#     )
#     print(data_string)
#         # print(len(data_string))
#     # else:
#     #     print("no connection")
print("++++++++++++++++++++++ Done connection! ++++++++++++++++++++++++++++")
import time

from src.utils.helper import check_received_angles, clear_input_buffer

# values = "11 1 545 5 384 6 10000 100"
# values = f" {110654} {545} {5} {10000} {100} "
values = [11.654, 0.005, 0.03, 10000, 100]
packed_data = struct.pack("f" * len(values), *values)
clear_input_buffer(object)
status = ""
while status != "done":
    # object.write(bytes(values, "utf-8"))
    object.write(packed_data)
    string = object.read_until().decode("utf-8").strip()
    time.sleep(2)
    print(string)
    status = string
# send_succ = False
# while not send_succ:
#     object.write(bytes(values, "utf-8"))
#     try:
#         status = object.read_until()
#     except:
#         status = ""
#     send_succ = True if status == "done" else False

# while not recv_succ:
#     recv_succ, angles_data = check_received_angles(object)
#     if recv_succ:
#         # logger.info(f">>> Angles data recieved: {angles_data}")
#         print(angles_data)
