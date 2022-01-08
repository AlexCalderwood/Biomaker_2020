from camera_utils import initialise_MIR, get_camera_port
import cv2
import numpy as np

try:
    MIR_PORT = get_camera_port("PureThermal")
    MIRCamera = initialise_MIR()
    while True:
        MIRimg = MIRCamera.grab(MIR_PORT)  # cv2 Video can only take 8-bit frames - could do maths to convert temp to 0-255
        MIRimg = 255*((MIRimg - MIRimg.min())/(MIRimg.max()-MIRimg.min()))
        MIRimg = MIRimg.astype(np.uint8)
        MIRimg = cv2.resize(MIRimg, None, fx=4, fy=4, interpolation=cv2.INTER_AREA)
        cv2.imshow("MIR Camera", MIRimg)

        c = cv2.waitKey(0)
        if c != -1:
            break
finally:
    MIRCamera.release()
