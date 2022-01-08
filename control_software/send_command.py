from serial_utils import open_serial, send_request, read_reply
from time import sleep
import sys
print("ALL LIGHTS AT ALL RANGES ARE DANGEROUS. Wear acceptable eye protection with near-infrared protection, as IR is invisible.")
print()


def constrain(val, min_val, max_val):
    """ Forces any number to be inside a given range. Numbers outside are set to the limits.
    """
    return min(max_val, max(min_val, val))
    

def run(cmd):
    try:
        print("Please wait, this may take a few seconds.")
        ser = open_serial("/dev/ttyACM0")
        sleep(2)
        send_request(ser, data)
        print(read_reply(ser))
    except Exception as e:
        print(e)
    finally:
        ser.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("Sending command")
        data = [constrain(int(x), 0, 65535) for x in sys.argv[1:]]
        print("Are you sure you want to send this command? y/n")
        print(data)
        inp = input()
        if inp == "y":        
            run(data)
        else:
            print("Command aborted.")
    else:
        print("Insufficient parameters provided.")

