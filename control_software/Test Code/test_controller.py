import cv2
import picamera
import picamera.array
import time



NIR_PORT = 0
MIR_PORT = 2

NIRCamera = cv2.VideoCapture(NIR_PORT)
if not NIRCamera.isOpened():
    raise IOError(f"Cannot open NIR camera on port {NIR_PORT}")

MIRCamera = cv2.VideoCapture(MIR_PORT)
if not MIRCamera.isOpened():
    raise IOError(f"Cannot open MIR camera on port {MIR_PORT}")

picam = picamera.PiCamera(resolution=(3280,2464))
picam.rotation = 90
picam.exposure_compensation = -25
picam.start_preview()
time.sleep(2)

try:
    while True:
        NIRimg = NIRCamera.read()
        NIRimg = cv2.resize(NIRimg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow("NIR", NIRimg)

        MIRimg = MIRCamera.read()
        MIRimg = cv2.resize(MIRimg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow("NIR", MIRimg)

        NIRimg = NIRCamera.read()
        NIRimg = cv2.resize(NIRimg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imshow("NIR", NIRimg)

        with picamera.array.PiRGBArray(picam) as stream:
            picam.capture(stream, format='bgr')
            # At this point the image is available as stream.array
            RGBimg = stream.array
            cv2.imshow("RBG", RGBimg)


        c = cv2.waitKey(1)
        if c == 27:
            break


finally:
    picam.stop_preview()
    picam.close()
    NIRCamera.release()
    MIRCamera.release()
    cv2.destroyAllWindows()