import serial


############# SERIAL DATA HANDLING #######################


def open_serial(port, baudrate=9600, timeout=1):
    """ Returns an opened and flushed serial port
    """
    ser = serial.Serial(port, baudrate, timeout=timeout)
    ser.flushInput()
    return ser


def send_request(ser, request_data):
    """ Sends list of UNSIGNED integers via serial, least-significant-byte first
    """

    # Send data
    for element in request_data:
        if element is not None:
            while element > 255:         # While there is more than one byte left to send
                element, next_smallest_byte = divmod(element, 256)      # Divide by 256 to get dividend (MSBytes) and remainder (LSByte)
                ser.write(bytes([next_smallest_byte]))
            ser.write(bytes([element]))  # Send int request
        else:
            ser.write(bytes([255,255]))  # Send alternative two bytes


def read_buffer(ser):
    """Reads data from serial buffer and returns list of unsigned 16-bit integers
    """
    received_data = []
    reply_lengths = [                                                   # Excluding primary key (PK) at start of each message
        # 0. Set lights, [et, dB]
        2,
        # 1. Set temperature, [et, dB]
        2,
        # 2. Read temperature, [T0, T1, T2, T3, T4, T5, et, dB]
        8,
        # 3. Set CFI procedure, [et, dB]
        2,
        # 4. Trigger CFI, [et, dB]
        2,
        # 5. Enable/disable LEDs, [et, dB]
        2,
        # 6. Enable/disable bed-peltiers, [et, dB]
        2
    ]
    nextBytes = ser.read(2)
    if len(nextBytes) == 2:                         # If first 16-bit int has been received
        pk = int.from_bytes(nextBytes, "little")    # Decode first int, the PK of the response
    else:
        return None                                 # Message has not been received
    
    for x in range(reply_lengths[pk-1]):
        nextBytes = ser.read(2)                     # Read next 16-bit int
        if len(nextBytes) == 2:                     # If next 16-bit int has been received
            nextInt = int.from_bytes(ser.read(2), "little") # Translate bytes
            if nextInt == 65535:
                received_data.append(None)                  # 65355 is reserved value meaning erroneous value
            else:
                received_data.append(nextInt)
        else:
            received_data.append(None)              # Two bytes were not received

    return received_data
