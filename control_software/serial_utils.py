import serial
from datetime import datetime


def open_serial(port, baudrate=9600, timeout=1):
    """ Returns an opened and flushed serial port
    """
    ser = serial.Serial(port, baudrate, timeout=timeout)
    ser.flushInput()
    return ser


def generate_package(send_time="", data=""):
    """ Takes in time of generation and data to generate a string of all data in appropriate format
    """
    if send_time == "":
        send_time = datetime.now().strftime("%H:%M:%S")

    return str(send_time) + data


def read_serial_data(ser):
    ser_bytes = ser.readline()  # Read request
    if len(ser_bytes) > 0:  # If any data have been received
        return ser_bytes.decode("utf-8")  # Decode the data from binary
    else:
        return "No data"


def run():

    ser = open_serial("COM4")

    while True:
        try:
            input()

            package = generate_package(data=", Hss")
            ser.write(package.encode("utf-8"))  # Send request as the time
            print("Request sent at", datetime.now().strftime("%H:%M:%S"))
            ser_bytes = read_serial_data(ser)
            print(ser_bytes)

        except Exception as e:
            print(e)
            print("Keyboard Interrupt")
            ser.close()
            break


if __name__ == "__main__":
    
    run()