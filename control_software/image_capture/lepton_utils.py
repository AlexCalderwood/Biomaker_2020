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
    """Class to access Lepton Camera."""
    
    lepton_exe = "~/RaspberryPi/lepton_data_collector/./lepton_data_collector"
    

    def __init__(self, raw_dir, img_dir):
        """ Constructor
        """
        self.set_raw_dir(raw_dir)
        self.set_img_dir(img_dir)
    
    
    def set_raw_dir(self, raw_dir):
        raw_dir = str(raw_dir)
        if raw_dir[-1] != "/":
            raw_dir += "/"
        self.raw_dir = raw_dir

    
    def set_img_dir(self, img_dir):
        img_dir = str(img_dir)
        if img_dir[-1] != "/":
            img_dir += "/"
        self.img_dir = img_dir


    def generate_raw_img(self, raw_dir=None, raw_name="frame_", images=1):
        """ Instructs lepton camera to take a number of images,
            and saves them in raw directory as "<raw_name>xxxxxx.GRAY"
        """
        if not raw_dir:
            raw_dir = self.raw_dir

        os.system(self.lepton_exe + f" -3 -c {images} -o " + raw_dir + raw_name)


    def convert_raw_img(self, raw_dir=None, raw_img_name="frame_000000.gray"):
        """ Converts raw .GRAY file to a (120x160) np array of 'int16's
        """
        if not raw_dir:
            raw_dir = self.raw_dir

        raw_image = np.fromfile(raw_dir+raw_img_name, dtype='>i2')  # Read as int16, BIG ENDIAN
        raw_image.shape = (120,160)
        return raw_image

    
    def generate_img_array(self, raw_dir=None, raw_name="frame_"):
        """ Obtains a new image from attached lepton camera, and converts it to np array
        """
        if not raw_dir:
            raw_dir = self.raw_dir
        
        self.generate_raw_img(raw_dir, raw_name)
        return self.convert_raw_img(raw_dir, str(raw_name) + "000000.gray")


    def preview(self):

        fig, ax = plt.subplots(1,1)
        image = self.generate_img_array(raw_name="frame_1")
        im = ax.imshow(image, cmap='gray')

        while True:
            image = self.generate_img_array(raw_name="frame_1")  # frame_1 used for previews, frame_0 used for data
            im.set_data(image)
            fig.canvas.draw_idle()
            plt.pause(1)
