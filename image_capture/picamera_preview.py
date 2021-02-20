from picamera_utils import init_picamera

def run():
    picam = init_picamera()
    picam.start_preview()
    input()
    picam.stop_preview()
    return 0


if __name__ == "__main__":
    run()
