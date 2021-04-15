#!/usr/bin/env python

from preprocessor_functions import *

### transform the dummy IR images generated back!

scriptd = sys.path[0]
playingd = scriptd + '/registration_playing/'

for file in os.listdir(playingd):
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

    imgRef, imgTest = prep_images_for_align(origRef, origTest,
                                            filterGreen=True, sharpenIR=True)
    print(imgRef.shape)
    show_pics([imgRef, imgTest])

    ### TODO:
    # this homography align works well with dummy, but not real IR images -
    # try some of the more constrained alignments at :!!!
    # https://learnopencv.com/image-alignment-ecc-in-opencv-c-python/
    out = feature_align(imgRef, imgTest,
                        maxFeatures=3000, keepFraction=0.3,
                        DEBUG=True)

    refFeatures = out['refImgFeatures']
    imgFeatures = out['testImgFeatures']
    matchedVis = out['matchedFeatures']
    alignedImg = out['alignedImg']

    out = ecc_align(imgRef, imgTest, 'HOMOGRAPHY')
    eccImg = out['alignedImg']
    #show_pics([imgRef, imgTest, eccImg])

    # make single image showing features found, and features matched:
    p_refFeatures, p_imgFeatures, p_matchedVis = pad_image_height([refFeatures,
                                                                   imgFeatures,
                                                                   matchedVis])
    mappingPic = np.hstack((p_refFeatures, p_imgFeatures, p_matchedVis))
    cv2.imwrite(f'{playingd}/{outstr}_mapping.JPG',mappingPic)

    # make image showing input, output, and overlay images:
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
    cv2.imwrite(f'{playingd}/{outstr}_in_out.JPG', outPic)
