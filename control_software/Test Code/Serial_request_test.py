import serial
from datetime import datetime
from time import sleep



# Open serial connection to port COM4, baudrate:9600b/s, with a timeout of 1 second to avoid hanging
ser = serial.Serial("COM4", 9600, timeout=1)
sleep(3)
# Clear any erroneous data already in the buffer (memory in the PC where arduino sends the data)
ser.flushInput()

recipe_data = [datetime.now(), 1, 25, 124, None, 213]

while True:
    try:
        input()
        formatted_data = recipe_data[:]
        formatted_data[0] = formatted_data[0].strftime("%Y-%m-%d %H:%M:%S")
        del formatted_data[1]  # Logging status not sent to arduino
        if recipe_data[1]:  # A request accompanied by photos being taken (turn the white lights on)
            formatted_data.append(254)  # Turn white light intensity to max
            formatted_data.append(5)  # 5 seconds before white lights turn off again
        else:
            formatted_data.append(0)  # Turn white light intensity to 0
            formatted_data.append(0)  # No light timeout needed
        print(formatted_data)

        # Send data
        #print("Request:", formatted_data[0].encode("utf-8"), bytes(formatted_data[1:]))
        ser.write(formatted_data[0].encode("utf-8"))  # Send string request
        for element in formatted_data[1:]:
            if not (element is None):
                ser.write(bytes([element]))  # Send int request
            else:
                ser.write(bytes([255]))  # Send alternative 1 byte
        print("request sent!")
        ser_bytes = ser.read(32)  # Read request
        if len(ser_bytes) > 0:  # If any data have been received
            print(ser_bytes[:19].decode("utf-8"))  # Decode the data from binary
            print([b for b in ser_bytes[19:]])
        else:
            print("No data received! :(")
            
    except Exception as e:
        ser.close()
        raise e
        #print(e)
        #print("Keyboard Interrupt")
        #ser.close()
        break