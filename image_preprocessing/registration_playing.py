#!/usr/bin/env python
from preprocessor_functions import *

scriptd = sys.path[0]
playingd = scriptd + '/registration_playing/'
origPath = playingd + 'original.JPG'


### transform them back!
imgRef = img
imgTest = IR_like # dst, smallDst, IR_like
outstr = 'IR_like'
align_to = 'IR' # string flag for how align_images should treat alignment.
                # "IR" if aligning to IR like image.

# align_images expects 3-channel images, and are needed for overlay
if len(imgTest.shape) == 2:
    imgTest = cv2.merge((imgTest, imgTest, imgTest))

out = align_images(imgRef, imgTest, maxFeatures=3000, keepFraction=0.3,
                   align_to='IR')

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
