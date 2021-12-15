from flirpy.camera.lepton import Lepton
import cv2
import numpy as np

with Lepton() as camera:
    while True:
        img = camera.grab().astype(np.float32)
        print("min", img.min(), img.min()/100 - 269.65)
        print("max", img.max(), img.max()/100 - 269.65)
        print()
        #img = 255*((img - 29000)/(31000-29000))
        img = 255*((img - img.min())/(img.max()-img.min()))
        img = img.astype(np.uint8)
        #print("min", img.min())
        #print("max", img.max())
        #print(img[0][0])
        #print(type(img[0][0]))
        img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_AREA)
        cv2.imshow('Lepton', img)
        if cv2.waitKey(1) == 27:
            break

cv2.destroyAllWindows()