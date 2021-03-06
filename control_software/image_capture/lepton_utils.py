import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from time import sleep


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


def get_image_array(img_name):
    capture_image("~/Biomaker/Biomaker_2020/image_capture/raw_imgs/" + str(img_name))
    return convert_raw_img("raw_imgs/", str(img_name) + "000000.gray")


def preview_lepton():

    fig, ax = plt.subplots(1,1)
    image = get_image_array("frame_1")
    im = ax.imshow(image, cmap='gray')

    while True:
        image = get_image_array("frame_1")  # frame_1 used for previews, frame_0 used for data
        im.set_data(image)
        fig.canvas.draw_idle()
        plt.pause(1)
