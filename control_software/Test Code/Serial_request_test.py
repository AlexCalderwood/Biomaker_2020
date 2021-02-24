import serial
from datetime import datetime

# Open serial connection to port COM4, baudrate:9600b/s, with a timeout of 1 second to avoid hanging
ser = serial.Serial("COM4", 9600, timeout=1)

# Clear any erroneous data already in the buffer (memory in the PC where arduino sends the data)
ser.flushInput()

while True:
    try:
        input()
        request_time = datetime.now().strftime("%H:%M:%S")  # Get time that data was requested (current time)
        ser.write(request_time.encode("utf-8"))  # Send request as the time
        print("request sent!")
        ser_bytes = ser.readline()  # Read request
        if len(ser_bytes) > 0:  # If any data have been received
            print(ser_bytes.decode("utf-8"))  # Decode the data from binary
        else:
            print("No data received! :(")
    except Exception as e:
        print(e)
        print("Keyboard Interrupt")
        ser.close()
        break