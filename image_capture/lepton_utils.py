import numpy as np
import matplotlib.pyplot as plt
PATH = "C:/Users/Finns/Desktop/yrmp tpi/Images/"
IMAGE_PATH = PATH +"frame_000049_2.gray"
raw_image = np.fromfile(IMAGE_PATH, dtype=np.uint16)
raw_image.shape = (120,160)
print(raw_image[0][0:10])
plt.imshow(raw_image,cmap = 'gray')
plt.imsave("pi.png", raw_image, cmap='gray')
plt.show()