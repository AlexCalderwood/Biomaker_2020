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
NIR_ENABLED = False
MIR_ENABLED = True

NIR_exposure = 16
start = time.time()




if NIR_ENABLED:
    NIRCamera = cv2.VideoCapture(NIR_PORT)
    if not NIRCamera.isOpened():
        raise IOError(f"Cannot open NIR camera on port {NIR_PORT}")
    NIRCamera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    NIRCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    videoWriter = cv2.VideoWriter('testvid.avi', fourcc, 12.0, (1920, 1080))

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
    time.sleep(2)
    picam.awb_mode = 'off'
    picam.awb_gains = (1.61, 1.61)
    picam.shutter_speed = 30596





print("Objects created")

ser = open_serial("/dev/ttyACM0")

print("Serial connection opened")

data = conv_funcs = ["2021-12-14 00:00:00",
                  False,
                  20,
                  0,
                  0,
                  50,
                  0,
                  False]
request_env_data(ser, data)
env_data = read_env_data(ser)

print("Instructions sent")





def set_picamera_gains(picamera, ser, target, targ_error):
    brightness = 0
    DGerror = abs(picamera.digital_gain - target)
    AGerror = abs(picamera.analog_gain - target)
    smallest_error = DGerror + AGerror
    while True:
        time.sleep(0.5)
        request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 0, brightness, 0, False])
        DGerror = picamera.digital_gain
        AGerror = picamera.analog_gain
        new_error = DGerror + AGerror
        if abs(DGerror) < targ_error and abs(AGerror) < targ_error:
            picamera.exposure_mode = 'off'
            return 0
        elif new_error > (smallest_error*1.1):
            picamera.exposure_mode = 'off'
            return 1
        elif new_error < smallest_error:
            smallest_error = new_error
        brightness += 1

blue = False
brightness = 0
exposure = 31273

EXPOSURE_SET = False
take_picture = False





try:
    while True:

        
        if NIR_ENABLED:
            Nstart = time.time()
            _, NIRimg = NIRCamera.read()
            videoWriter.write(NIRimg)
            print(time.time() - Nstart)
            #cv2.imshow("NIR", NIRimg)
            #print(np.amax(NIRimg), time.time()-start)

        if MIR_ENABLED:
            _, MIRimg = MIRCamera.read()
            MIRimg = cv2.resize(MIRimg, None, fx=4, fy=4, interpolation=cv2.INTER_AREA)
            cv2.imshow("MIR", MIRimg)
        
        if RGB_ENABLED:
            print(picam.digital_gain, "d")
            print(picam.analog_gain)
            
            if not EXPOSURE_SET:
                dgError = abs(picam.digital_gain - 1)
                agError = abs(picam.analog_gain - 1)
                if (dgError < 0.1) and (agError < 0.1):
                    picam.exposure_mode = 'off'
                    EXPOSURE_SET = True
                    print("Exposure set")
            
            if take_picture:
                if toggle_color:
                    if blue:
                        request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 54, 0, 0, False])
                        print("IR")
                        blue = False
                        color = "I"
                    else:
                        request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 0, 0, 54, False])
                        print("RED")
                        blue = True
                        color = "R"
                    toggle_color = False
                    start = time.time()
                elif time.time() - start > 0.5:
                    newstart = time.time()
                    picam.capture(f"{color}54.data", 'yuv')
                    print(time.time() - newstart)
                    print(f"{color}54.yuv captured")
                    take_picture = False
                    
        
        

        c = cv2.waitKey(1)
        if c == 27:     # ESC
            break
        elif c == 10:   # RETURN
            if False:
                brightness += 10
                request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 0, brightness, 0, False])
                print(brightness)
            if False:
                if blue:
                    request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 54, 0, 0, False])
                    print("blue")
                    blue = False
                else:
                    request_env_data(ser, ["2021-12-14 00:00:00", False, 20, 0, 0, 0, 54, False])
                    print("red")
                    blue = True
            if False:
                take_picture = True
                toggle_color = True
                        
        
        

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