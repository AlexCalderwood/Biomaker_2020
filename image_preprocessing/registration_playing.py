#!/usr/bin/env python
from preprocessor_functions import *

scriptd = sys.path[0]
playingd = scriptd + '/registration_playing/'
origPath = playingd + 'original.JPG'


### Make some dummy images to see if can transform back...

# read the original image
img = cv2.imread(origPath)

# genrate some images with
# arbitrary perspective transformation
img_h, img_w, cols = img.shape
pts1 = np.float32([[56,65],[img_w-300,52],[28,img_h+400],[img_w + 200,img_h + 300]])
pts2 = np.float32([[0,0],[img_w,0],[0,img_h],[img_w,img_h]])
M = cv2.getPerspectiveTransform(pts1,pts2)
dst = cv2.warpPerspective(img, M, img.shape[0:2])
#show_pics([img, dst])
cv2.imwrite(playingd+'tranformed.JPG',dst)

# low resolution and transformed
downsample_factor = 15
smallDst = cv2.resize(dst, (int(img_w / downsample_factor), int(img_h / downsample_factor)))
cv2.imwrite(playingd+'tranformed-small.JPG', smallDst)

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
cv2.imwrite(playingd+'IR_like.JPG',small_blurred)
# show_pics([smallDst, mask_sanity, small_grey, small_blurred])


### transform them back!
imgRef = img
imgTest = smallDst # dst, smallDst, small_blurred
outstr = 'transformed-small'

# do the alignment

# downsample reference image to same resolution as the test image
#imgRef = to_same_resolution(imgTest, imgRef)

out = align_images(imgRef, imgTest, maxFeatures=3000, keepFraction=0.3)
refFeatures = out['refImgFeatures']
imgFeatures = out['testImgFeatures']
matchedVis = out['matchedFeatures']
alignedImg = out['alignedImg']

# pad heights so can show in one window
# intermediate images of feature points aligned
p_refFeatures, p_imgFeatures, p_matchedVis = pad_image_height([refFeatures,
                                                               imgFeatures,
                                                               matchedVis])
mappingPic = np.hstack((p_refFeatures, p_imgFeatures, p_matchedVis))
cv2.imwrite(f'{playingd}/{outstr}_mapping.JPG',mappingPic)


# make nice output image to compare inputs, output, aligned image, and the
# overlay of input and aligned
# resize small test image to same size as high resolution one
bigImgTest = to_same_resolution(imgRef, imgTest)

# make overlay of refernce and aligned image
overlay = make_overlay(imgRef, alignedImg)

# pad the heights
p_imgRef, p_imgTest, p_alignedImg, p_overlay = pad_image_height([imgRef,
                                                      bigImgTest,
                                                      alignedImg,
                                                      overlay])

# combine all the images & and write to file
outPic = np.hstack((p_imgRef, p_imgTest, p_alignedImg, p_overlay))
cv2.imwrite(f'{playingd}/{outstr}_in_out.JPG', outPic)
