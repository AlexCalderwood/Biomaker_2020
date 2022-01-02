from serial_utils import send_request
import cv2
import picamera
import picamera.array
from flirpy.camera.lepton import Lepton
import numpy as np
import re
import os
from time import sleep


############# RGB, NIR, MIR CAMERA HANDLING #######################


def get_camera_port(camera_name):
    """ Function to determine camera device number based on name of device - takes in string and matches to v4l2 devices
    """
    cam_num = None
    for file in os.listdir("/sys/class/video4linux"):                                       # Search through list of device files available to RPi
        real_file = os.path.realpath("/sys/class/video4linux/" + file + "/name")
        if os.path.exists(real_file):                                                       # If device has a file called "name"
            with open(real_file, "rt") as name_file:
                name = name_file.read().rstrip()                                            # Open the file, and extract the name of the device
            if camera_name in name:                                                         # If the desired name is present
                cam_num = int(re.search("\d+$", file).group(0))                             # extract the one-or-more (+) digits (\d) followed by an end-line ($) from the folder name
                return cam_num - 1                                                          # Each devices has two consecutive numbers, larger is found first - we need the smaller
        else:
            return -1                                                                       # Failed to find any port


def initialise_NIR(NIR_PORT, exposure_absolute=16, resolution=(1920,1080)):
    """ Function to intialise NIR camera with approproate parameters - returns the cv2 VideoCapture object
    """
    NIRCamera = cv2.VideoCapture(NIR_PORT)                                                  # Access camera
    if not NIRCamera.isOpened():
        raise IOError(f"Cannot open NIR camera on port {NIR_PORT}")

    NIRCamera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])                                  # Set hoizontal resolution
    NIRCamera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])                                 # Set vertical resolution

    # For some reason this is essential for setting exposure (and takes ~0.5 seconds...)
    _, NIRimg = NIRCamera.read()                                                            # Must be called beforehand ?? to actually set the exposure
    os.system(f"v4l2-ctl -d {NIR_PORT} -c exposure_absolute={exposure_absolute}")           # -d specifies device, -c sets parameter
    os.system(f"v4l2-ctl -d {NIR_PORT} -c exposure_absolute={exposure_absolute}")           # Must be set at least twice??
    for x in range(5):                                                                      # Takes about 5 reads to sink in !!??!
        _, NIRimg = NIRCamera.read()

    return NIRCamera                                                                        # Return camera object


def initialise_MIR():
    """ Function to initialise MIR camera, returns flirpy object
        Unable to set appropriate parameters...
    """
    return Lepton()


def initialise_RGB(resolution=(3296,2464), rotation=90, exposure_compensation=-25, awb_mode='off', awb_gains=(1.61, 1.61), shutter_speed=30596):
    """ Function to initialise RGB Picamera with appropriate parameters (except digital+analog gains) and returns picamera object
    """
    picam = picamera.PiCamera(resolution=resolution) # Set picam resolution
    picam.rotation = rotation                        # Set image orientation
    picam.exposure_compensation = exposure_compensation # Set brightness of image
    #picam.start_preview(fullscreen=False, window=(100, 20, 640, 480))
    sleep(2)
    picam.awb_mode = awb_mode                        # Set how awb gains are set
    picam.awb_gains = awb_gains                      # Set auto-white-balance gains (red,blue), fractions between 0 and 8
    picam.shutter_speed = shutter_speed              # Setting shutter speed sets exposure_time in us (must be synced to LED freq.)
    return picam


def set_picamera_gains(picamera, ser, target, targ_error, initial_brightness=0, error_cutoff=1.1, brightness_increment=1):
    """ Function to set RGB Picamera digital and analog gains
        They cannot be set manually, only frozen once set automatically.
        Function ramps up white lights until gains both reach g~target, with total abs. error of less than target_error, error starts to increase too far.
    """
    brightness = initial_brightness
    DGerror = abs(picamera.digital_gain - target)
    AGerror = abs(picamera.analog_gain - target)
    smallest_error = DGerror + AGerror                                  # Calculate initial error
    while True:
        sleep(0.5)                                                 # Pause to allow lights to set and camera to adjust.
        send_request(ser, [1, 0, 0, brightness, 0])
        DGerror = abs(picamera.digital_gain - target)
        AGerror = abs(picamera.analog_gain - target)
        new_error = DGerror + AGerror                                   # Calculate new error
        if abs(DGerror) < targ_error and abs(AGerror) < targ_error:     # If within acceptable distance
            picamera.exposure_mode = 'off'                              # Freeze gains
            return 0                                                    # Return success
        elif new_error > (smallest_error*error_cutoff):                 # If error grows too much beyond latest minimum error
            picamera.exposure_mode = 'off'                              # Cut losses and freeze gain (IMPROVE THIS TO RETURN TO MINIMUM???)
            return 1                                                    # Return fail
        elif new_error < smallest_error:                                # Check for local minimum error
            smallest_error = new_error
        brightness += brightness_increment                              # If still searching, iterate brightness


# CREATE BASE CAMERA CLASS, THEN CREATE CLASSES FOR EACH TYPE OF CAMERA (FOR UNIFORMITY)
# INITIALISE
# (SET EXPOSURE, ONLY RGB)
# TAKE PICTURE
# RECORD VIDEO
# CLOSE