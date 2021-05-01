import PySimpleGUI as sg


def autofill_datetimes(data):
    """ Takes in start, end, number, interval values and calculates any missing one (if applicable)
    """
    missing = None
    new_data = data[:]
    clean_data = data[:]
    autofill_functions = [  # Functions to calculate the corresponding index they occupy
        lambda : data[1] - (data[2] * data[3]),
        lambda : data[0] + (data[2] * data[3]),
        lambda : (data[1] - data[0]) / data[3],
        lambda : (data[1] - data[0]) / data[2]
    ]

    if data.count(None) > 1:  # Too many unknowns
        pass
    elif data.count(None) == 0:  # No unknowns
        pass
    else:
        missing = data.index(None)  # Location of the one unknown
        new_data[missing] = autofill_functions[missing]()  # Fill unknown using corresponding function
        clean_data = [convert_value(param) for param in new_data]

    return clean_data, missing

    
def convert_value(value):
    """Takes in string and returns appropriate datatype for interpretation
    """
    if value == "":
        return None
    elif value == ".":
        return None
    elif float(value).is_integer():
        return int(value)
    else:
        return float(value)


def validate_str_input(old_text, new_text, whitelist=None, char_limits=None, block_multichar=True):
    """Validate string inputs based on characters and length
    """
    if block_multichar and (len(new_text) - len(old_text) > 1):
            print("multichar abort")
            return old_text  # More than one new character (e.g. copypaste), so reject entirely

    if char_limits and len(new_text) != 0:
        if len(new_text) > char_limits[1] or len(new_text) < char_limits[0]:
            print("char_limits abort", char_limits)
            return old_text
    if whitelist:
        for char in new_text:
            if char not in whitelist:
                print("whitelist abort", char, whitelist)
                return old_text
    
    return new_text


def validate_numeric_input(old_text, new_text, whitelist=None, char_limits=None, block_multichar=True, round_ints=True):#value_limits=None, round_ints=True):
    """Validate string inputs based on numeric values
    """
    new_text = validate_str_input(old_text, new_text, whitelist, char_limits, block_multichar)
    if new_text == old_text:
        return old_text

    """if value_limits and len(new_text) != 0:
        try:
            new_value = float(new_text)
        except:
            print("float convert abort", new_text)
            return old_text
        if new_value < value_limits[0] or new_value > value_limits[1]:
            print("value limit abort", new_value, value_limits)
            return old_text

        if round_ints:
            return str(round_to_int(new_value))
    
        return str(new_value)"""
    
    return new_text


def round_to_int(value):
    """Takes in string and returns appropriate datatype for interpretation
    """
    if value == "":
        return 0  # This will get annoying!
    elif value == ".":
        return 0
    elif float(value).is_integer():
        return int(value)
    else:
        return float(value)


def update_on_outfocus(old_text, new_text, value_limits=None, round_ints=True):
    """Update the value of a text-box to be inside its limits when the user clicks off
    """
    if value_limits and len(new_text) != 0:
        try:
            new_value = float(new_text)
        except:
            print("float convert abort", new_text)
            return old_text
        if new_value < value_limits[0]:
            print("increased to lower", new_value, value_limits[0])
            return str(value_limits[0])
        elif new_value > value_limits[1]:
            print("reduced to upper", new_value, value_limits[1])
            return str(value_limits[1])
        elif round_ints:
            return str(round_to_int(new_value))
        else:
            return str(new_value)
    return new_text
        


def run():
    
    gipt = lambda key, size: sg.InputText(key=key, enable_events=True, size=size)  # Generic InputText

    layout = [
        [sg.Text("Test Start:")],
        [sg.CalendarButton('Date', close_when_date_chosen=False, target="-DATE-", format="%Y-%m-%d", ),
        sg.Text("Time (24h)")],
        [gipt("-DATE-", (10,1)), gipt("-HOURS-", (2,1)), sg.Text(":"), gipt("-MINUTES-", (2,1)), sg.Text(":"), gipt("-SECONDS-", (2,1))],
        [sg.Text("Imaging:")],
        [sg.Text("Start"), sg.Text("End"), sg.Text("Number"), sg.Text("Interval")],
        [gipt("-START-", (4,1)), gipt("-END-", (4,1)), gipt("-NUMBER-", (4,1)), gipt("-INTERVAL-", (4,1)), sg.Button("Calculate")],
        [sg.Text("Temperature:")],
        [sg.Text("Temp")],
        [gipt("-TEMP-", (4,1))],
        [sg.Text("Lighting:")],
        [sg.Text("Red"), sg.Text("White"), sg.Text("Blue")],
        [gipt("-RED-", (3,1)), gipt("-WHITE-", (3,1)), gipt("-BLUE-", (3,1))],
        [sg.Button("Save")]
    ]

    window = sg.Window("Recipe Creator", layout, finalize=True)

    window['-HOURS-'].bind('<FocusOut>', 'OUTFOCUS')  # Bind tkinter FocusOut event to these elements - when keyboard focus moves off
    window['-MINUTES-'].bind('<FocusOut>', 'OUTFOCUS')
    window['-SECONDS-'].bind('<FocusOut>', 'OUTFOCUS')
    window['-TEMP-'].bind('<FocusOut>', 'OUTFOCUS')
    window['-RED-'].bind('<FocusOut>', 'OUTFOCUS')
    window['-WHITE-'].bind('<FocusOut>', 'OUTFOCUS')
    window['-BLUE-'].bind('<FocusOut>', 'OUTFOCUS')

    # Default states of all elements
    old_values = {'Date': '',
                '-DATE-': '',
                '-HOURS-': '',
                '-MINUTES-': '',
                '-SECONDS-': '',
                '-START-': '',
                '-END-': '',
                '-NUMBER-': '',
                '-INTERVAL-': '',
                '-TEMP-': '',
                '-RED-': '',
                '-WHITE-': '',
                '-BLUE-': ''}

    # Functions with prespecified parameters for each element, determining valid input data
    input_handlers = {'Date': None,
                '-DATE-': lambda : validate_str_input(old_values["-DATE-"], new_values["-DATE-"], whitelist="1234567890-", char_limits=(0,10), block_multichar=False),
                '-HOURS-': lambda : validate_numeric_input(old_values["-HOURS-"], new_values["-HOURS-"], whitelist="1234567890", char_limits=(0,2)),
                '-MINUTES-': lambda : validate_numeric_input(old_values["-MINUTES-"], new_values["-MINUTES-"], whitelist="1234567890", char_limits=(0,2)),
                '-SECONDS-': lambda : validate_numeric_input(old_values["-SECONDS-"], new_values["-SECONDS-"], whitelist="1234567890", char_limits=(0,2)),
                '-START-': None,
                '-END-': None,
                '-NUMBER-': None,
                '-INTERVAL-': None,
                '-TEMP-': lambda : validate_numeric_input(old_values["-TEMP-"], new_values["-TEMP-"], whitelist="1234567890.", char_limits=(0,4)),
                '-RED-': lambda : validate_numeric_input(old_values["-RED-"], new_values["-RED-"], whitelist="1234567890", char_limits=(0,3)),
                '-WHITE-': lambda : validate_numeric_input(old_values["-WHITE-"], new_values["-WHITE-"], whitelist="1234567890", char_limits=(0,3)),
                '-BLUE-': lambda : validate_numeric_input(old_values["-BLUE-"], new_values["-BLUE-"], whitelist="1234567890", char_limits=(0,3))}

    # Acceptable value limits for numeric inputs, used for updating when the user clicks off a field
    outfocus_limits = {'Date': None,
                '-DATE-': None,
                '-HOURS-': (0,24),
                '-MINUTES-': (0,59),
                '-SECONDS-': (0,59),
                '-START-': None,
                '-END-': None,
                '-NUMBER-': None,
                '-INTERVAL-': None,
                '-TEMP-': (0,40),
                '-RED-': (0,254),
                '-WHITE-': (0,254),
                '-BLUE-': (0,254)}


    while True:
        event, new_values = window.read()
        if event == sg.WIN_CLOSED or event == "Save":  # Check exit events
            break

        if event in old_values:  # If it is a classical event
            if input_handlers[event] is not None:  # If there needs to be input validation
                new_input = input_handlers[event]()  # Call prespecified input validation function
                window[event].update(new_input)  # Update UI
                new_values[event] = new_input  # Update local list of values
        elif len(event) > 8:
            if event[-8:] == "OUTFOCUS":  # If it is an outfocus event (appended by OUTFOCUS)
                event = event[:-8]  # Remove OUTFOCUS footer
                new_input = update_on_outfocus(old_values[event], new_values[event], outfocus_limits[event])
                if event in ['-HOURS-', '-MINUTES-', '-SECONDS-'] and len(new_input) == 1:  # If its a time, and has only 1 digit
                    new_input = "0" + new_input  # Add a 0 onto the front, e.g. 00:00, 03:08
                window[event].update(new_input)  # Update UI
                new_values[event] = new_input  # Update local list of values

        if event in ["temp", "red", "white", "blue"] and values[event]:  # Check special inputs are valid (0-254)
            if int(values[event]) < 0:
                window[event].update(0)
            elif int(values[event]) > 254:
                window[event].update(254)
            else:
                window[event].update(int(values[event]))
        elif event == "Calculate":
            keys = ["start", "end", "number", "interval"]
            img_params = [convert_value(values[key]) for key in keys]  # Convert UI entries to useful datatypes
            img_params, changed = autofill_datetimes(img_params)  # Calculate any missing value
            if not (changed is None):  # If something has been changed (calculated)
                window[keys[changed]].update(img_params[changed])  # Update the UI with the change

        print("event", event)
        old_values = new_values

    if event == "Save":
        pass


if __name__ == "__main__":
    run()
