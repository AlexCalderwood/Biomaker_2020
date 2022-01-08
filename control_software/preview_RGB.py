import cv2
from camera_utils import initialise_RGB, set_picamera_gains
from time import sleep

try:
    print("Opening camera preview...")
    RGBCamera = initialise_RGB()
    RGBCamera.start_preview(fullscreen=False, window=(100, 20, 640, 480))
    input("Press return to stop the preview.")
    RGBCamera.stop_preview()
finally:
    RGBCamera.close()
