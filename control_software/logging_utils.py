import datetime
import os
from time import sleep


def convert_recipe_line(line):
    """ Converts line (as a string) from recipe file to a list of relevent types according to latest format
    
    1. time (%y-%m-%d-%H:%M:%S date)    - time to read this instruction
    2. log (Bool)                       - whether to log data for this instruction or just write conditions
    3. temp (int)                       - temperature condition to write

    """
    # Splits string into relevent variables (still as strings)
    data = line.split(", ")
    
    # Empty strings (blank lines) will be parsed as [""]
    if data == [""]:
        raise ValueError("Empty line parsed from recipe file")

    # List of conversion functions based on latest format
    conv_funcs = [lambda datestr: datetime.datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S"),
                  bool,
                  float]

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
                dirname = dirname[:-4]  # Remove the previous footer
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

    with open(f"{path}{dirname}/{dirname}.txt", "a") as datafile:
        datafile.write(data_string + "\n")  # Write data with a newline character on the end
    print(f"data saved to {path}{dirname}!")


def format_data_string(data):
    """ Converts data to string format for writing to log file
    Similar formatting but not necessarily the same as recipe file!

    1. time_logged (%y-%m-%d-%H:%M:%S date)    - time data was logged
    3. current_temp (int)                      - temperature at time of log

    """
    data_string = data[0].strftime("%y-%m-%d %H:%M:%S")  # Convert datetime to string

    for val in data[1:]:  # Convert all other simple data to string
        data_string += ", "
        data_string += str(val)
        
    return data_string  # Return string version of data for writing


def request_rgb_image():
    sleep(1)
    print("RGB image retrieved!")
    return 0


def request_lepton_image():
    sleep(1)
    print("IR image retrieved!")
    return 0


def request_env_data():
    sleep(1)
    print("Env. data retrieved!")
    return 0
