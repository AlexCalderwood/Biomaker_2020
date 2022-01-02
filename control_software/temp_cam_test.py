import cv2
from time import sleep
import picamera

    


def set_picamera_gains2(picam):
    dgError = abs(picam.digital_gain - 1)
    agError = abs(picam.analog_gain - 1)
    if (dgError < 0.1) and (agError < 0.1):
        picam.exposure_mode = 'off'
        print("Exposure set")
        return True
    else:
        return False

    
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
        time.sleep(0.5)                                                 # Pause to allow lights to set and camera to adjust.
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


def run():
    RGBCamera = initialise_RGB()
    print("awb gains:", RGBCamera.awb_gains)
    EXPOSURE_SET = False
    try:
        while True:
            RGBCamera.start_preview(fullscreen=False, window=(100,20,640,480))
            print("This")
            if not EXPOSURE_SET:
                EXPOSURE_SET = set_picamera_gains2(RGBCamera)
    finally:
        RGBCamera.close()


if __name__ == "__main__":
    run()
