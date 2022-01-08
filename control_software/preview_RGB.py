import cv2
from camera_utils import initialise_RGB, set_picamera_gains
from time import sleep

try:
    RGBCamera = initialise_RGB()
    RGBCamera.start_preview()
    input()
    RGBCamera.stop_preview()
finally:
    RGBCamera.close()
