#!/usr/bin/env python
from preprocessor_functions import *

scriptd = sys.path[0]
playingd = scriptd + '/registration_playing/'
origPath = playingd + 'original.JPG'


    ### Make some dummy images to see if can transform back...
for file in os.listdir(playingd):
    print(file)
    if file[0:3] != 'RGB':
        continue

    outfile = 'IR' + file[3:]

    origPath = playingd + file
    outPath = playingd + outfile

    # read the original image
    img = cv2.imread(origPath)

    # genrate some images with
    # arbitrary perspective transformation
    img_h, img_w, cols = img.shape

    pts1 = np.float32([[56,65],[img_w-300,52],[28,img_h+400],[img_w + 200,img_h + 300]])
    #pts1 = np.float32([[0,0],[img_w,0],[0,img_h],[img_w,img_h]])
    pts2 = np.float32([[0,0],[img_w,0],[0,img_h],[img_w,img_h]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    dst = cv2.warpPerspective(img, M, (img_w, img_h))
    #cv2.imwrite(playingd+'tranformed.JPG', dst)

    # low resolution and transformed
    downsample_factor = 15
    smallDst = cv2.resize(dst, (int(img_w / downsample_factor), int(img_h / downsample_factor)))
    #cv2.imwrite(playingd+'tranformed-small.JPG', smallDst)

    # low resolution and plants only (more or less like expect actual IR to be)
    hsv = cv2.cvtColor(smallDst, cv2.COLOR_BGR2HSV)
    lower = np.array([20, 80, 0])
    upper = np.array([50, 255, 200])
    greenMask = cv2.inRange(hsv, lower, upper)
    mask_sanity = cv2.bitwise_and(smallDst, smallDst, mask=greenMask)
    small_grey = cv2.cvtColor(mask_sanity, cv2.COLOR_BGR2GRAY)
    small_blurred = cv2.resize(cv2.blur(small_grey, (3, 3)),
                              (int(img_w / downsample_factor),
                              int(img_h / downsample_factor)))
    #cv2.imwrite(playingd+'small_grey.JPG', small_grey)
    IR_like = small_blurred

    cv2.imwrite(outPath, IR_like)
    #show_pics([dst, smallDst, mask_sanity, small_grey, small_blurred])
