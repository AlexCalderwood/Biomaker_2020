import serial

# Open serial connection to port COM4, baudrate:9600b/s, with a timeout of 1 second to avoid hanging
ser = serial.Serial("COM4", 9600, timeout=1)

# Clear any erroneous data already in the buffer (memory in the PC where arduino sends the data)
ser.flushInput()

while True:
    try:
        ser_bytes = ser.readline()
        if len(ser_bytes) > 0:  # If any data has been received
            print(ser_bytes[:-2].decode("utf-8"))  # Decode the data from binary
    except Exception as e:
        print(e)
        print("Keyboard Interrupt")
        ser.close()
        break