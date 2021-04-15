from datetime import datetime
import os
from time import sleep
from serial_utils import open_serial, generate_rpi_request, read_serial_data, convert_env_string


def convert_recipe_line(line):
    """ Converts line (as a string) from recipe file to a list of relevent types according to latest format
    
    1. time (%y-%m-%d-%H:%M:%S date)    - time to read this instruction
    2. log (Bool)                       - whether to log data for this instruction or just write conditions
    3. target_temp (int)                - temperature condition to write
    4. R (int8)                         - Intensity of red light
    5. Y (int8)                         - Intensity of yellow light
    6. B (int8)                         - Intensity of blue light

    """
    # Splits string into relevent variables (still as strings)
    data = line.split(", ")
    
    # Empty strings (blank lines) will be parsed as [""]
    if data == [""]:
        raise ValueError("Empty line parsed from recipe file")

    # List of conversion functions based on latest format
    conv_funcs = [lambda datestr: datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S"),
                  bool,
                  int,
                  int,
                  int,
                  int]

    for i in range(len(data)):
        try:
            data[i] = conv_funcs[i](data[i])  # Call corresponding function on ith element
        except ValueError:
            print("Failed to convert", data[i], "position", i)
            data[i] = None  # Any corrupt data is assigned None
            continue  # Carry on converting rest of data
    return data


def create_new_dir(path, dirname):
    """ Creates a new directory - appends (n) if directory already exists
    """

    footer = 0
    while True:
        if os.path.exists(path + dirname):
            footer += 1
            if footer != 1:  # If this isnt the first time updating the name
                dirname = dirname[:17]  # Remove the previous footer
            dirname += (f" ({footer})")  # Add latest footer to string
        else:
            break  # Continue to create directory

    os.makedirs(path + dirname)
    #print(f"new folder \'{path}{dirname}\' created!")
    return dirname


def save_data(path, dirname, data):
    """ Saves data to preprogammed location, inside its own new directory.
    The name of the new directory is the first time entry of the recipe + a unique footer as required
    """
    data_string = format_data_string(data)
    #print("log_string", data_string)

    with open(f"{path}{dirname}/{dirname}.txt", "a") as datafile:
        datafile.write(data_string + "\n")  # Write data with a newline character on the end
    #print(f"data saved to {path}{dirname}!")


def format_data_string(env_data):
    """ Converts env_data (as a list) to a string to write to logfile
        
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

    data_string = ""

    if not (env_data[0] is None):
        data_string += datetime.strftime(env_data[0], "%Y-%m-%d %H:%M:%S")
    for i in range(7, len(env_data)-2):  # Record only time-of-request, and 8-12 inclusive
        data_string += ", "
        if not(env_data[i] is None):
            data_string += str(env_data[i])
    
    return data_string


def request_env_data(ser, request_data):

    # Convert data to serializable form
    formatted_data = request_data[:]
    formatted_data[0] = formatted_data[0].strftime("%Y-%m-%d %H:%M:%S")
    del formatted_data[1]  # Logging status not sent to arduino
    if request_data[1]:  # A request accompanied by photos being taken (turn the white lights on)
        formatted_data.append(254)  # Turn white light intensity to max
        formatted_data.append(5)  # 5 seconds before white lights turn off again
    else:
        formatted_data.append(0)  # Turn white light intensity to 0
        formatted_data.append(0)  # No light timeout needed

    # Send data
    ser.write(formatted_data[0].encode("utf-8"))  # Send string request
    for element in formatted_data[1:]:
        if not (element is None):
            ser.write(bytes([element]))  # Send int request
        else:
            ser.write(bytes([255]))  # Send alternative 1 byte


def read_env_data(ser):
    """Reads env_data from serial buffer and returns list of useful data"""
    data_length = 32  # Expected number of bytes to be in buffer
    env_bytes = ser.read(32)  # Timeout set when ser was initialised
    env_data = []
    if len(env_bytes) > 0:
        env_data.append(datetime.strptime(env_bytes[:19].decode("utf-8"), "%Y-%m-%d %H:%M:%S"))  # Read time/datestamp
        env_data += [None if b == 255 else b for b in env_bytes[19:]]
    else:
        env_data = [None] * 13

    return env_data
