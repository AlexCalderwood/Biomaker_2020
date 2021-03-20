import datetime
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
    conv_funcs = [lambda datestr: datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S"),
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
    print(f"new folder \'{path}{dirname}\' created!")
    return dirname


def save_data(path, dirname, rgb_image, ir_image, data):
    """ Saves data to preprogammed location, inside its own new directory.
    The name of the new directory is the first time entry of the recipe + a unique footer as required
    """
    data_string = format_data_string(data)
    print("log_string", data_string)

    with open(f"{path}{dirname}/{dirname}.txt", "a") as datafile:
        datafile.write(data_string + "\n")  # Write data with a newline character on the end
    print(f"data saved to {path}{dirname}!")


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
        data_string += datetime.datetime.strftime(env_data[0], "%Y-%m-%d %H:%M:%S")
    for i in range(7, len(env_data)-2):  # Record only time-of-request, and 8-12 inclusive
        data_string += ", "
        if not(env_data[i] is None):
            data_string += str(env_data[i])
    
    return data_string


def request_rgb_image():
    sleep(1)
    print("RGB image retrieved!")
    return 0


def request_lepton_image():
    sleep(1)
    print("IR image retrieved!")
    return 0


def request_env_data(request_data):

    # Interpret data
    rpi_request = generate_rpi_request(request_data)
    print("rpi request:", rpi_request)

    ser = open_serial("COM4")
    try:
        sleep(3)  # FIX THIS
        ser.write(rpi_request.encode("utf-8"))  # Send request as the time
        print("Request sent at", datetime.datetime.now().strftime("%H:%M:%S"))
        env_string = read_serial_data(ser)
        ser.close()
        print("env_string:", env_string)
    except Exception as e:
        print(e)
        ser.close()
        return 1

    env_data = convert_env_string(env_string)

    return env_data
