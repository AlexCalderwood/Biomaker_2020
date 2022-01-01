from logging_utils import convert_recipe_line, create_new_dir, save_data, send_request, read_env_data
from serial_utils import open_serial
import serial
from time import sleep

def send_request(ser, request_data):
    """ Sends list of UNSIGNED integers via serial, least-significant-byte first
    """

    # Send data
    for element in request_data:
        if element is not None:
            while element > 255:         # While there is more than one byte left to send
                element, next_smallest_byte = divmod(element, 256)      # Divide by 256 to get dividend (MSBytes) and remainder (LSByte)
                ser.write(bytes([next_smallest_byte]))
            ser.write(bytes([element]))  # Send int request
        else:
            ser.write(bytes([255,255]))  # Send alternative two bytes

def run():
    ser = serial.Serial("COM10", 9600, timeout=1)
    ser.flushInput()
    sleep(2)
    try:
        input = [1027]
        send_request(ser, input)
        #ser.write(bytes([4,3,255]))
        output = int.from_bytes(ser.read(2), "little")
        print(output)
    finally:
        ser.close()



if __name__ == "__main__":
    run()
