import serial
import time

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

    written = 0
    # Send data
    for element in request_data:
        if element is not None and element >= 0:
            if element <= 255:                  # If value would be interpreted as just one byte
                ser.write(bytes([element,0]))   # Send in two-byte format
                written += 2
            else:
                MSBs, LSB = divmod(element, 256)
                elementBytes = [LSB]
                while MSBs > 255:         # While there is more than one byte left to send
                    MSBs, LSB = divmod(MSBs, 256)      # Divide by 256 to get dividend (MSBytes) and remainder (LSByte)
                    elementBytes.append(LSB)
                elementBytes.append(MSBs)                                    # Add remaining MSB
                ser.write(bytes(elementBytes))                                 # Send remaining MSB
                written += len(elementBytes)
        else:
            ser.write(bytes([255,255]))  # Send alternative two bytes if value is missing (None)
            written += 2
    return written                                                          # Returns number of bytes sent


def read_reply(ser):
    """Reads data from serial buffer and returns list of unsigned 16-bit integers
    """
    reply_lengths = [                                                   # Excluding primary key (PK) at start of each message
        # 0. Read diagnostics, [target_temp, B, I, W, R, CFI, LEDs, BPLRs, et, dB]
        10,
        # 1. Set lights, [et, dB]
        2,
        # 2. Set temperature, [et, dB]
        2,
        # 3. Read temperature, [T0, T1, T2, T3, T4, T5, et, dB]
        8,
        # 4. Set CFI procedure, [et, dB]
        2,
        # 5. Trigger CFI, [et, dB]
        2,
        # 6. Enable/disable LEDs, [et, dB]
        2,
        # 7. Enable/disable bed-peltiers, [et, dB]
        2
    ]
    nextBytes = ser.read(2)
    if len(nextBytes) == 2:                         # If first 16-bit int has been received
        pk = int.from_bytes(nextBytes, "little")    # Decode first int, the PK of the response
        received_data = [pk]
    else:
        print("No reply")
        return None                                 # Message has not been received
    if pk == 65535:
        received_data = [None]
        incomingInts = 2                           # If arduino has received erroneous PK, will still reply [et,dB] (this is its own unique reply, but no corresponding request)
    else:
        incomingInts = reply_lengths[pk]
    for x in range(incomingInts):
        nextBytes = ser.read(2)                     # Read next 16-bit int
        if len(nextBytes) == 2:                     # If next 16-bit int has been received
            nextInt = int.from_bytes(nextBytes, "little") # Translate bytes
            if nextInt == 65535:
                received_data.append(None)                  # 65355 is reserved value meaning erroneous value
            else:
                received_data.append(nextInt)
        else:
            received_data.append(None)              # Two bytes were not received

    return received_data


def run():
    ser = open_serial("COM5")
    time.sleep(2)
    try:
        # Send request
        #print("sent:", send_request(ser, [4, 220] + [1,2,3,4,5]*100))
        print("sent:", send_request(ser, [7, 0]))
        print(read_reply(ser))

        # Read diagnostics
        print("Diagnostics")
        send_request(ser, [0])
        print(read_reply(ser))
    finally:
        ser.close()

if __name__ == "__main__":
    run()
