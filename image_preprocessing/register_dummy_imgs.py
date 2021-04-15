#!/usr/bin/env python
from preprocessor_functions import *

### transform the dummy IR images generated back!

scriptd = sys.path[0]
playingd = scriptd + '/registration_playing/'

for file in ['RGB5_2021-04-08T11-09-51_cropped.jpg']: #os.listdir(playingd):
    print(file)
    if file[0:3] != 'RGB':
        continue

    fileRoot = file[3:-3]

    # load the RGB, and IR images
    RGBPath = playingd + file
    IRPath = playingd + 'IR' + fileRoot + 'png'

    origRef = cv2.imread(RGBPath)
    origTest = cv2.imread(IRPath)
    outstr = file[3:]

    # prep images for alignment: get same resolution, filter for green,
    # sharpenIR up etc
    imgRef, imgTest = prep_images_for_align(origRef, origTest,
                                            filterGreen=False,
                                            highlightGreen=True,
                                            sharpenIR=False)

    p_imgRef, p_imgTest = pad_image_height([imgRef, imgTest])
    outPic = np.hstack((p_imgRef, p_imgTest))
    cv2.imwrite(f'{playingd}/{outstr}_alignment_prepped.JPG', outPic)

    # ORB algorithm for feature alignment
    out = feature_align(imgRef, imgTest,
                        maxFeatures=3000, keepFraction=0.3,
                        DEBUG=False)

    refFeatures = out['refImgFeatures']
    imgFeatures = out['testImgFeatures']
    matchedVis = out['matchedFeatures']
    alignedImg = out['alignedImg']

    # ECC algorithm for alignment
    out = ecc_align(imgRef, imgTest, 'HOMOGRAPHY') # ' AFFINE' or 'HOMOGRAPHY')
    eccImg = out['alignedImg']
    # show_pics([imgRef, imgTest, eccImg])


    # Make combined output images

    # make single image showing features found, and features matched:
    p_refFeatures, p_imgFeatures, p_matchedVis = pad_image_height([refFeatures,
                                                                   imgFeatures,
                                                                   matchedVis])
    mappingPic = np.hstack((p_refFeatures, p_imgFeatures, p_matchedVis))
    cv2.imwrite(f'{playingd}/{outstr}_featureMapping.JPG',mappingPic)

    # make image showing input, output, and overlay images:
    # For ORB aligned image:
    # resize the (small) aligned image up to the reference image size
    alignedImg = cv2.resize(alignedImg, (origRef.shape[1], origRef.shape[0]))
    # combine to 3 channel, so can concatenate with BGR images
    alignedImg = cv2.merge((alignedImg, alignedImg, alignedImg))
    # resize small IR image to same size as high resolution one
    bigImgTest = to_same_resolution(origRef, origTest)
    # make overlay of refernce and aligned image
    overlay = make_overlay(origRef, alignedImg)
    # pad the heights
    p_imgRef, p_imgTest, p_alignedImg, p_overlay = pad_image_height([origRef,
                                                          bigImgTest,
                                                          alignedImg,
                                                          overlay])
    # combine all the images & and write to file
    outPic = np.hstack((p_imgRef, p_imgTest, p_alignedImg, p_overlay))
    cv2.imwrite(f'{playingd}/{outstr}_in_out_ORB.JPG', outPic)

    # for ECC aligned image:
    eccImg = cv2.resize(eccImg, (origRef.shape[1], origRef.shape[0]))
    # combine to 3 channel, so can concatenate with BGR images
    eccImg = cv2.merge((eccImg, eccImg, eccImg))
    # resize small IR image to same size as high resolution one
    bigImgTest = to_same_resolution(origRef, origTest)
    # make overlay of refernce and aligned image
    eccOverlay = make_overlay(origRef, eccImg)
    # pad the heights
    p_imgRef, p_imgTest, p_alignedImg, p_overlay = pad_image_height([origRef,
                                                          bigImgTest,
                                                          eccImg,
                                                          eccOverlay])
    # combine all the images & and write to file
    outPic = np.hstack((p_imgRef, p_imgTest, p_alignedImg, p_overlay))
    cv2.imwrite(f'{playingd}/{outstr}_in_out_ECC.JPG', outPic)
