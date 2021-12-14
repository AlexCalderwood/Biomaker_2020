import cv2
import picamera
import picamera.array
import time
from logging_utils import request_env_data, read_env_data
from serial_utils import open_serial
import numpy as np
import os

print("Starting test controller...")

NIR_PORT = 2
MIR_PORT = 0

RGB_ENABLED = False
NIR_ENABLED = True
MIR_ENABLED = False

NIR_exposure = 32
start = time.time()

if NIR_ENABLED:
    NIRCamera = cv2.VideoCapture(NIR_PORT)
    if not NIRCamera.isOpened():
        raise IOError(f"Cannot open NIR camera on port {NIR_PORT}")
    
    # For some reason this is essential (and takes ~0.5 seconds...)
    _, NIRimg = NIRCamera.read()  # Must be called beforehand ?? to actually set the exposure
    os.system(f"v4l2-ctl -d 2 -c exposure_absolute={NIR_exposure}")
    os.system(f"v4l2-ctl -d 2 -c exposure_absolute={NIR_exposure}")  # Must be set at least twice??
    for x in range(5):  # Takes about 5 reads to sink in !!??!
        _, NIRimg = NIRCamera.read()


if MIR_ENABLED:
    MIRCamera = cv2.VideoCapture(MIR_PORT)
    if not MIRCamera.isOpened():
        raise IOError(f"Cannot open MIR camera on port {MIR_PORT}")

if RGB_ENABLED:
    picam = picamera.PiCamera(resolution=(3296,2464))
    picam.rotation = 90
    picam.exposure_compensation = -25
    picam.start_preview(fullscreen=False, window=(100, 20, 640, 480))

print("Objects created")

ser = open_serial("/dev/ttyACM0")

print("Serial connection opened")

data = conv_funcs = ["2021-12-14 00:00:00",
                  False,
                  20,
                  0,
                  0,
                  0,
                  0,
                  False]
request_env_data(ser, data)
env_data = read_env_data(ser)
blue = False
print("Instructions sent")

#for x in range(10):
#    os.system(f"v4l2-ctl -d 2 -c exposure_absolute={NIR_exposure}")
try:
    while True:
            
        if NIR_ENABLED:
            _, NIRimg = NIRCamera.read()
            cv2.imshow("NIR", NIRimg)
            print(np.amax(NIRimg), time.time()-start)
            


        if MIR_ENABLED:
            _, MIRimg = MIRCamera.read()
            MIRimg = cv2.resize(MIRimg, None, fx=4, fy=4, interpolation=cv2.INTER_AREA)
            cv2.imshow("MIR", MIRimg)
            

        c = cv2.waitKey(1)
        if c == 27:     # ESC
            break
        elif c == 10:   # RETURN
            if False:
                NIRCamera.set(cv2.CAP_PROP_EXPOSURE, NIR_exposure)
                for i in range(2):
                    _, NIRimg = NIRCamera.read()
                    print("''", np.amax(NIRimg), time.time() - start)
                print(NIR_exposure)
                NIR_exposure += 1
            if False:
                NIRCamera.set(cv2.CAP_PROP_AUTO_EXPOSURE, NIR_auto)
                print(NIR_auto)
                NIR_auto = 0
            if False:
                NIRCamera.set(cv2.CAP_PROP_GAIN, NIR_gain)
                print(NIR_gain)
                NIR_gain += 0.1
            if False:
                request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 240, 0, 0, 0, False])
            if False:
                cv2.imwrite("test-13.png", NIRimg)
                print(np.amax(NIRimg), time.time() - start)
            if True:
                if blue:
                    request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 240, 0, 0, 0, False])
                    print("blue")
                    blue = False
                else:
                    request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 0, 0, 60, False])
                    print("red")
                    blue = True
                        
        
        

finally:
    print("Test finished")
    if RGB_ENABLED:
        picam.stop_preview()
        picam.close()
    if NIR_ENABLED:
        NIRCamera.release()
    if MIR_ENABLED:
        MIRCamera.release()
    cv2.destroyAllWindows()
    request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 0, 0, 0, False])
    ser.close()