import numpy as np
import matplotlib.pyplot as plt
import os
from time import sleep

"""
PATH = "C:/Users/Finns/Desktop/yrmp tpi/Images/"
IMAGE_PATH = PATH +"frame_000049_2.gray"
raw_image = np.fromfile(IMAGE_PATH, dtype=np.uint16)
raw_image.shape = (120,160)
print(raw_image[0][0:10])
plt.imshow(raw_image,cmap = 'gray')
plt.imsave("pi.png", raw_image, cmap='gray')
plt.show()
"""

def capture_image(dest):
    os.system("~/RaspberryPi/lepton_data_collector/./lepton_data_collector -3 -c 1 -o " + dest)

def prepend_byte(loc, raw):
    with open(loc+raw,'rb') as f:
        with open(loc+"prepended_"+raw,'wb') as f2:
            f2.write("0".encode())
            f2.write(f.read())

def convert_raw_img(loc, raw):
    prepend_byte(loc, raw)
    raw_image = np.fromfile(loc+"prepended_"+raw, dtype=np.uint16)
    raw_image.shape = (120,160)
    return raw_image

def close_event():
    plt.close()

if __name__ == "__main__":

    while True:
        capture_image("~/Biomaker/Biomaker_2020/image_capture/raw_imgs/frame_")
        print("Raw image captured!")

        raw_image = convert_raw_img("raw_imgs/", "frame_000000.gray")
        print("Raw image converted!")

        plt.imshow(raw_image, cmap='gray')
        fig = plt.figure()
        timer = fig.canvas.new_timer(interval = 5000)
        timer.add_callback(close_event)
        timer.start()
        plt.show()
        
    #plt.imsave("imgs/frame_000000.png", raw_image, cmap='gray')
    #print("Image saved!")

