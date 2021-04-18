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


def run():
    
    layout = [
        [sg.Text("Recipe name:")],
        [sg.InputText("recipe_0")],
        [sg.Text("Imaging:")],
        [sg.Text("Start"), sg.Text("End"), sg.Text("Number"), sg.Text("Interval")],
        [sg.InputText(key="start", enable_events=True), sg.InputText(key="end", enable_events=True),
         sg.InputText(key="number", enable_events=True), sg.InputText(key="interval", enable_events=True),
         sg.Button("Calculate")],
        [sg.Text("Temperature:")],
        [sg.Text("Temp")],
        [sg.InputText(key="temp", enable_events=True)],
        [sg.Text("Lighting:")],
        [sg.Text("Red"), sg.Text("White"), sg.Text("Blue")],
        [sg.InputText(key="red", enable_events=True), sg.InputText(key="white", enable_events=True),
         sg.InputText(key="blue", enable_events=True)],
        [sg.Button("Save")]
    ]

    window = sg.Window("Recipe Creator", layout)
    while True:
        event, values = window.read()
        numerical_keys = ["start", "end", "number", "interval", "temp", "red", "white", "blue"]
        if event == sg.WIN_CLOSED or event == "Save":  # Check exit events
            break
        if event in numerical_keys and values[event]:  # Check necessarily numerical inputs are valid
            if not (values[event][-1] in "0123456789."):
                window[event].update(values[event][:-1])
                values[event] = values[event][:-1]
        if event in ["temp", "red", "white", "blue"] and values[event]:  # Check special inputs are valid (0-254)
            print(values[event])
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
    if event == "Save":
        sg.popup("Recipe saved as ", values[0])


if __name__ == "__main__":
    run()
