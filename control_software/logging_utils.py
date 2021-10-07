from datetime import datetime
import os
from time import sleep
from serial_utils import open_serial, generate_rpi_request, read_serial_data, convert_env_string


def convert_recipe_line(line):
    """ Converts line (as a string) from recipe file to a list of relevent types according to latest format
    
    1. time (%y-%m-%d-%H:%M:%S date)    - time to read this instruction
    2. log (Bool)                       - whether to log data for this instruction or just write conditions
    3. target_temp (int)                - temperature condition to write
    4. B (int8)                         - Intensity of blue light
    5. I (int8)                         - Intensity of IR light
    6. W (int8)                         - Intensity of white light
    7. R (int8)                         - Intensity of red light
    8. trigger_CFI (bool)               - whether to trigger CFI or not

    """
    # Splits string into relevent variables (still as strings)
    data = line.split(", ")
    
    # Empty strings (blank lines) will be parsed as [""]
    if data == [""]:
        raise ValueError("Empty line parsed from recipe file")

    # List of conversion functions based on latest format
    conv_funcs = [lambda datestr: datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S"),
                  lambda x: bool(int(x)),
                  int,
                  int,
                  int,
                  int,
                  int,
                  lambda x: bool(int(x))]

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

    with open(f"{path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:
        datafile.write(data_string + "\n")  # Write data with a newline character on the end
    #print(f"data saved to {path}{dirname}!")


def format_data_string(env_data):
    """ Converts env_data (as a list) to a string to write to logfile
        
    1. target_temp (int8)                            - temperature condition to write
    2. B (int8)                                     - Intensity of red light
    3. I (int8)                                     - Intensity of yellow light
    4. W (int8)                                     - Intensity of blue light
    5. R (int8)                                     - Intensity of white light
    6. temp0  (int8)                                - Measured temperature 0
    7. temp1  (int8)                                - Measured temperature 0
    8. temp2  (int8)                                - Measured temperature 0
    9. temp3  (int8)                                - Measured temperature 0
    10. temp4  (int8)                               - Measured temperature 0
    11. temp5  (int8)                               - Measured temperature 0
    12. elapsed_time (int8)                         - Time since receiving last bit of request and sending reply
    13. dropped_bits (int8)                         - Bits of message lost (ideally should always be 0...)

    """

    data_string = ""

    for i in range(len(env_data)):  # Record only time-of-request, and 8-12 inclusive
        if not(env_data[i] is None):
            data_string += str(env_data[i])
        data_string += ", "
    data_string.strip(", ")
    return data_string


def request_env_data(ser, request_data):

    # Send data
    for element in request_data[2:]:
        if element is not None:
            ser.write(bytes([element]))  # Send int request
        else:
            ser.write(bytes([255]))  # Send alternative 1 byte


def read_env_data(ser):
    """Reads env_data from serial buffer and returns list of useful data"""
    data_length = 14  # Expected number of bytes to be in buffer
    env_bytes = ser.read(data_length)  # Timeout set when ser was initialised
    env_data = []
    if len(env_bytes) > 0:
        env_data += [None if b == 255 else b for b in env_bytes]
    else:
        env_data = [None] * 13

    return env_data
