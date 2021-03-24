from picamera import PiCamera

def run():
    with PiCamera() as picam:
        picam.rotation = 270
        picam.resolution = (3280, 2464)
        picam.start_preview()
        input()
        picam.stop_preview()
        picam.close()
        return 0


if __name__ == "__main__":
    run()
