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
cv2.imwrite(playingd+'tranformed-small.JPG',smallDst)

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

#show_pics([smallDst, mask_sanity, small_grey, small_blurred])


# transform them back!
# https://www.pyimagesearch.com/2020/08/31/image-alignment-and-registration-with-opencv/
# specify which image to transform back to imgRef
imgRef = img
imgTest = dst
outstr = 'transformed'
maxFeatures = 1000
keepFraction = 0.2

# convert both to black and white
refGrey = cv2.cvtColor(imgRef, cv2.COLOR_BGR2GRAY)
imgGrey = cv2.cvtColor(imgTest, cv2.COLOR_BGR2GRAY)

# use ORB to detect keypoints and extract local invariant features
orb = cv2.ORB_create(maxFeatures)
(kpsA, descsA) = orb.detectAndCompute(imgGrey, None)
(kpsB, descsB) = orb.detectAndCompute(refGrey, None)

# show the features
imgFeatures = cv2.drawKeypoints(imgGrey, kpsA, None, color=(0, 255, 0), flags=0)
refFeatures = cv2.drawKeypoints(refGrey, kpsB, None, color=(0,255,0), flags=0)
#show_pics([refFeatures, imgFeatures])

# match the features
method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
matcher = cv2.DescriptorMatcher_create(method)
matches = matcher.match(descsA, descsB, None)

# sort matches by their distance (smaller is more similar)
matches = sorted(matches, key=lambda x: x.distance)

# keep only the top matches
keep = int(len(matches) * keepFraction)
matches = matches[:keep]

# visualise the matched keypoints
matchedVis = cv2.drawMatches(refGrey, kpsA, imgGrey, kpsB, matches, None)
#show_pics([refFeatures, imgFeatures, matchedVis])

# record which keypoints map to each other
ptsA = np.zeros((len(matches), 2), dtype='float')
ptsB = np.zeros((len(matches), 2), dtype='float')
for (i, m) in enumerate(matches):
    ptsA[i] = kpsA[m.queryIdx].pt
    ptsB[i] = kpsB[m.trainIdx].pt

# compute the homography matrix between the matched points
(H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)

# use H to align the images
(h, w) = imgRef.shape[:2]
alignedImg = cv2.warpPerspective(imgTest, H, (w, h))


# pad images to same height for checking output
mx_ht = max(refFeatures.shape[0], imgFeatures.shape[0], matchedVis.shape[0])
p_refFeatures = cv2.copyMakeBorder(refFeatures, mx_ht - refFeatures.shape[0],
                                   0,0,0, cv2.BORDER_CONSTANT, value=[0,0,0])
p_imgFeatures = cv2.copyMakeBorder(imgFeatures, mx_ht - imgFeatures.shape[0],
                                   0,0,0, cv2.BORDER_CONSTANT, value=[0,0,0])
p_matchedVis = cv2.copyMakeBorder(matchedVis, mx_ht - matchedVis.shape[0],
                                   0,0,0, cv2.BORDER_CONSTANT, value=[0,0,0])

mx_ht = max(imgRef.shape[0], imgTest.shape[0], alignedImg.shape[0])
p_imgRef = cv2.copyMakeBorder(imgRef, mx_ht - imgRef.shape[0],
                              0,0,0, cv2.BORDER_CONSTANT, value=[0,0,0])
p_imgTest = cv2.copyMakeBorder(imgTest, mx_ht - imgTest.shape[0],
                              0,0,0, cv2.BORDER_CONSTANT, value=[0,0,0])
p_alignedImg = cv2.copyMakeBorder(alignedImg, mx_ht - alignedImg.shape[0],
                              0,0,0, cv2.BORDER_CONSTANT, value=[0,0,0])

# inputPic = np.hstack(imgRef, imgTest)
print(p_refFeatures.shape)
print(p_imgFeatures.shape)
print(p_matchedVis.shape)

mappingPic = np.hstack((p_refFeatures, p_imgFeatures, p_matchedVis))
outPic = np.hstack((p_imgRef, p_imgTest, p_alignedImg))

cv2.imwrite(f'{playingd}/{outstr}_mapping.JPG',mappingPic)
cv2.imwrite(f'{playingd}/{outstr}_in_out.JPG', outPic)
