from datetime import datetime
import os


############# RECIPE AND DATA FILE HANDLING #######################


def convert_recipe_line(line):
    """Converts line (as a string) from recipe file to a list [datetime, ints...]
    """

    # Splits string into relevent variables (still as strings)
    data = line.split(", ")
    
    # Empty strings (blank lines) will be parsed as [""]
    if data == [""]:
        raise ValueError("Empty line parsed from recipe file")

    # Date is always first element - converted from string to datetime
    data[0] = datetime.strptime(data[0], "%Y-%m-%d %H:%M:%S")

    # Rest of elements are converted to integer, or 'None' type if there is an error
    for i in range(1, len(data)):
        try:
            data[i] = int(data[i])
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
                dirname = dirname[:dirname.index("(")-1]  # Remove the previous footer and space
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
    print("datastring ",data_string)
    with open(f"{path}{dirname}/raw_data/{dirname}.tmp", "a") as datafile:
        datafile.write(data_string + "\n")  # Write data with a newline character on the end
    #print(f"data saved to {path}{dirname}!")


def format_data_string(env_data):
    """ Converts env_data (as a list) to a string to write to logfile
    """

    data_string = ""
    for i in range(len(env_data)):  # Record only time-of-request, and 8-12 inclusive
        data_string += str(env_data[i])
        data_string += ", "
    data_string = data_string.strip(", ")
    return data_string
