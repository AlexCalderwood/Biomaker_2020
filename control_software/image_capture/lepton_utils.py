import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
from time import sleep


def prepend_byte(loc, raw):
    with open(loc+raw,'rb') as f:
        with open(loc+"prepended_"+raw,'wb') as f2:
            f2.write("0".encode())
            f2.write(f.read())


class LeptonCamera:

    lepton_dir = "~/RaspberryPi/lepton_data_collector/./lepton_data_collector

    #"~/Biomaker/Biomaker_2020/image_capture/raw_imgs/"


    def __init__(self, raw_dir, img_dir):
        """ Constructor
        """
        self.raw_dir = raw_dir
        self.img_dir = img_dir
    
    
    def set_raw_dir(self, raw_dir):
        self.raw_dir = raw_dir

    
    def set_img_dir(self, img_dir):
        self.img_dir = img_dir


    def capture_image(self, raw_dir=self.raw_dir, raw_name="frame", images=1):
        """ Instructs lepton camera to take a number of images, and saves them in raw directory as "frame_xxxxxx.GRAY"
        """
        os.system(lepton_dir + f"-3 -c {images} -o " + raw_dir + raw_name)


    def convert_raw_img(self, raw_dir=self.raw_dir, raw_name):
        """ Converts raw .GRAY file to a (120x160) np array of 'int16's
        """
        raw_image = np.fromfile(raw_dir+raw_name, dtype='>i2')  # Read as int16, BIG ENDIAN
        raw_image.shape = (120,160)
        return raw_image

    
    def get_image_array(self, raw_dir=self.raw_dir, raw_name="frame"):
        """ Obtains a new image array from the attached lepton camera, and converts it to np array
        """
        self.capture_image(raw_dir, raw_name)
        return self.convert_raw_img(raw_dir, str(raw_name) + "000000.gray")


    def preview(self):

        fig, ax = plt.subplots(1,1)
        image = self.get_image_array(raw_name="frame_1")
        im = ax.imshow(image, cmap='gray')

        while True:
            image = self.get_image_array(raw_name="frame_1")  # frame_1 used for previews, frame_0 used for data
            im.set_data(image)
            fig.canvas.draw_idle()
            plt.pause(1)
