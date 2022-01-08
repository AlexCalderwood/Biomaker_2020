import cv2
import sys
import os
import numpy as np

def run(dataset, image_name):
    print("False colour scale will vary across images, even if the temperatures measured are different.")
    print("This viewer adjusts the image to show maximum contrast.")
    print("Temperature data can be retrieved from the raw image by dividing a given pixel's value by 100 (gives reading in Kelvin)")
    image_path = "recorded_data/" + dataset + "/raw_data/" + image_name

    try:
        MIRimg = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    except:
        raise ValueError("Invalid image or dataset combination:", image_name)
    if MIRimg is None:
        raise ValueError("Invalid image or dataset combination:", image_name)
    MIRimg = 255*((MIRimg - MIRimg.min())/(MIRimg.max()-MIRimg.min()))
    MIRimg = MIRimg.astype(np.uint8)
    MIRimg = cv2.resize(MIRimg, None, fx=4, fy=4, interpolation=cv2.INTER_AREA)
    cv2.imshow("MIR image", MIRimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        if os.path.exists("recorded_data/" + sys.argv[1]):
            run(str(sys.argv[1]), str(sys.argv[2]))
        else:
            print("Invalid dataset or image name:", sys.argv[1])
            print("Please provide the name of the folder the data is kept in. This will be of the format YYYY-MM-DD-HH_MM_SS (x)")
    elif len(sys.argv) == 2:
        print("Insufficient arguments given. Please provide both dataset and image names.")
    else:
        print("Please provide both the dataset name and the image name you wish to view: \"python3 view_MIR_image.py <dataset> <image>")
        print("This viewer will look in the folder: recorded_data/<dataset>/raw_data for the image.")