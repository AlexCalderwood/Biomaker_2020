from serial_utils import open_serial, send_request, read_reply
from time import sleep
import sys
print("ALL LIGHTS AT ALL RANGES ARE DANGEROUS. Wear acceptable eye protection with near-infrared protection, as IR is invisible.")
print()


def constrain(val, min_val, max_val):
    """ Forces any number to be inside a given range. Numbers outside are set to the limits.
    """
    return min(max_val, max(min_val, val))
    

def run(B,I,W,R):
    B = constrain(B, 0, 255)
    I = constrain(I, 0, 255)
    W = constrain(W, 0, 255)
    R = constrain(R, 0, 255)
    try:
        print("Please wait, this may take a few seconds.")
        ser = open_serial("/dev/ttyACM0")
        sleep(2)
        send_request(ser,[6,1])
        read_reply(ser)
        send_request(ser, [1,B,I,W,R])
        read_reply(ser)
        print("Lights set.")
        print("For safety reasons, lights will only be active when door is closed.")
    except Exception as e:
        print(e)
    finally:
        ser.close()


if __name__ == "__main__":
    if len(sys.argv) > 4:
        print("Setting lights...")
        run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        print("Insufficient parameters provided: \"python3 set_lights.py <Blue> <IR> <White> <Red>\"")
        print("Values range from 0-255, Values below ~50 may not be enough to activate some lights.")
