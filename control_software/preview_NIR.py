from camera_utils import initialise_NIR, get_camera_port
import cv2

try:
    NIR_PORT = get_camera_port("USB 2.0 Camera")
    NIRCamera = initialise_NIR(NIR_PORT, exposure_absolute=4800, resolutio=(640,480))
    while True:
        _, NIRimg = NIRCamera.read()
        NIRimg = cv2.rotate(NIRimg, cv2.ROTATE_180)
        cv2.imshow("NIR Camera", NIRimg)

        c = cv2.waitKey(0)
        if c != -1:
            break
finally:
    NIRCamera.release()
