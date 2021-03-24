from picamera import PiCamera
from time import sleep

def init_picamera():
    """ Returns camera object with pre-set parameters for biomaker cabinet.
    """
    print("INIT NOW")
    camera = PiCamera()
    camera.rotation = 270
    camera.resolution = (3280, 2464)
    return camera
