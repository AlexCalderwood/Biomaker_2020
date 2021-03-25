import serial
import datetime
from time import sleep
import datetime


def open_serial(port, baudrate=9600, timeout=1):
    """ Returns an opened and flushed serial port
    """
    ser = serial.Serial(port, baudrate, timeout=timeout)
    ser.flushInput()
    return ser


def generate_rpi_request(data):
    """ Converts data (as a list) to a string to send to arduino
    
    1. time (%y-%m-%d-%H:%M:%S date)    - time to read this instruction
    2. log (Bool)                       - whether to log data for this instruction or just write conditions
    3. target_temp (int)                - temperature condition to write
    4. R (int8)                         - Intensity of red light
    5. Y (int8)                         - Intensity of yellow light
    6. B (int8)                         - Intensity of blue light
    7. W (int)                          - Intensity of white light (only high if picture is being taken)
    8. W_timeout (int)                  - Time for white light to be on (to avoid having to send another request)

    """

    rpi_request = ""

    expected_lengths = [19,2,3,3,3]  # Expected length of data if it needs replacing with '?'

    if not (data[0] is None):
        rpi_request += datetime.datetime.strftime(data[0], "%Y-%m-%d %H:%M:%S")
    else:
        rpi_request += "?" * expected_lengths[0]
    
    for i in range(2, len(data)):  # From 2 to skip time and logging fields
        rpi_request += ", "
        if not(data[i] is None):
            rpi_request += str(data[i])  # Call corresponding function on ith element
        else:
            rpi_request += "?" * expected_lengths[i]  # Replace any uninterpreted data with '???' to maintain byte-count

    if data[1]:  # A request accompanied by photos being taken (turn the white lights on)
        rpi_request += ", 255"  # Turn white light intensity to max
        rpi_request += ", 5"  # 5 seconds before white lights turn off again
    else:
        rpi_request += ", 000"  # Turn white light intensity to max
        rpi_request += ", 0"  # 5 seconds before white lights turn off again

    return rpi_request


def read_serial_data(ser, timeout=10):
    """ Look for serial data in the buffer
    """
    read_start = datetime.datetime.now()
    ser_bytes = ser.readline()  # Read request
    while len(ser_bytes) <= 0 and (datetime.datetime.now()-read_start).total_seconds() < timeout:
        ser_bytes = ser.readline()
        print("Nothing yet")
    if len(ser_bytes) > 0:  # If any data have been received
        return ser_bytes.decode("utf-8")  # Decode the data from binary
    else:
        return "No data"


def convert_env_string(env_string):
    """ Converts reply from arduino (string) to a list of relevent types according to latest format
    
    1. time of request (%y-%m-%d-%H:%M:%S date)     - time to read this instruction
    2. target_temp (int)                            - temperature condition to write
    3. R (int8)                                     - Intensity of red light
    4. Y (int8)                                     - Intensity of yellow light
    5. B (int8)                                     - Intensity of blue light
    6. W (int)                                      - Intensity of white light
    7. W_t (int)                                    - White timeout
    8. current_temp_high (int)                      - Measured temperature of top sensor
    9. current_temp_low (int)                       - Measured temperature of bottom sensor
    10. current_humid_high (int)                    - Measured humidity of top sensor
    11. current_humid_low (int)                     - Measured humidity of bottom sensor
    12. light_level (int)                           - Measured light level
    13. elapsed_time (int)                          - Time since receiving last bit of request and sending reply
    14. dropped_bits (int)                          - Bits of message lost (ideally should always be 0...)

    """
    # Splits string into relevent variables (still as strings)
    env_data = env_string.split(", ")

    # List of conversion functions based on latest format
    conv_funcs = [lambda datestr: datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S"),
                  int,
                  int,
                  int,
                  int,
                  int,
                  float,
                  float,
                  float,
                  float,
                  float,
                  float,
                  float,
                  float]

    for i in range(len(env_data)):
        try:
            env_data[i] = conv_funcs[i](env_data[i])  # Call corresponding function on ith element
        except ValueError:
            print("Failed to convert", env_data[i], "position", i)
            env_data[i] = None  # Any corrupt data is assigned None
            continue  # Carry on converting rest of data
    return env_data


def run():

    ser = open_serial("COM4")

    while True:
        try:
            input()

            package = "2021-03-17 22:21:00, 25, 125, 125, 125, 255, 5"#generate_rpi_request(data=", H")
            ser.write(package.encode("utf-8"))  # Send request as the time
            print("Request sent at", datetime.datetime.now().strftime("%H:%M:%S"))
            ser_bytes = read_serial_data(ser)
            print(ser_bytes)

        except Exception as e:
            print(e)
            print("Keyboard Interrupt")
            ser.close()
            break


#if __name__ == "__main__":
    
    #run()
