#!/usr/bin/env python
from preprocessor_functions import *


# path to directory containg images to process
scriptd = sys.path[0]
in_dir = scriptd + '/example_input/'
out_dir_ROI = scriptd + '/example_output/ROIs/'
out_dir_sanity = scriptd + '/example_output/intermediate/'


out_width = 500  # px width of output segmented imgs
out_height = 500

setup_dirs([in_dir, out_dir_sanity, out_dir_ROI])


### read the images and calculate timeseries order
imgs = read_images(in_dir, 'RGB')
img_timeseries_order = get_image_order(imgs) # get filenames ordered by time
ir_imgs = read_images(in_dir, 'IR')
# print(imgs.keys())
# print(img_timeseries_order)
# print(ir_imgs.keys())
# show_pics(imgs['RGB8_2021-04-08T11-09-51.jpg'])
# show_pics(ir_imgs['IR7_2021-04-08T11-09-51.png'])

##### START OF ALIGNMENT PLAYING ######
### align the RGB and IR iamges
# for each key in imgs, if an equivalent IR image exists,
# align them!

# get equivalent RGB and IR filenames
for f in imgs.keys():
    if f.startswith('RGB'):
        f_IR = f.replace('RGB', 'IR', 1)  # replace first "RGB" only

    if f_IR in ir_imgs.keys():

        # check that equivalent images
        # show_pics(imgs[f] + ir_imgs[f_IR])

        # do the alignment!
        # following
        # https://www.pyimagesearch.com/2020/08/31/image-alignment-and-registration-with-opencv/
        RGBimg = imgs[f][0]
        IRimg = ir_imgs[f_IR][0]
        IR_h = IRimg.shape[0]
        IR_w = IRimg.shape[1]
        print(f'IR resolution : {IR_h}, {IR_w}')

        # def align_images(RGBimg, IRimg, maxFeatures=500, keepPercent=0.2,
        # debug=True):
        # convert both the grayscale (probably should have edge detection instead?)
        hsv = cv2.cvtColor(RGBimg, cv2.COLOR_BGR2HSV)
        lower_light = np.array([20, 80, 0])
        upper_light = np.array([50, 255, 200])
        greenMask = cv2.inRange(hsv, lower_light, upper_light)
        mask_sanity = cv2.bitwise_and(RGBimg, RGBimg, mask=greenMask)
        #show_pics([RGBimg, mask_sanity])

        RGBGrey = cv2.cvtColor(mask_sanity, cv2.COLOR_BGR2GRAY)
        IRGrey = cv2.cvtColor(IRimg, cv2.COLOR_BGR2GRAY)

        smallRGBGrey = cv2.resize(RGBGrey, (IR_w, IR_h))

        #show_pics([RGBGrey, IRGrey, smallRGBGrey])

        # user ORB to detect keypoint and extract local invariant features
        maxFeatures = 500
        orb = cv2.ORB_create(maxFeatures)
        (kpsA, descsA) = orb.detectAndCompute(smallRGBGrey, None)
        (kpsB, descsB) = orb.detectAndCompute(IRGrey, None)

        # draw the images and keypoints
        RGBKeyImg = cv2.drawKeypoints(smallRGBGrey, kpsA, None,
                                 color=(0, 255, 0), flags=0)
        IRKeyImg = cv2.drawKeypoints(IRGrey, kpsB, None,
                                 color=(0,255,0), flags=0)
        show_pics([smallRGBGrey, RGBKeyImg, IRGrey, IRKeyImg])
        print(junk)

        # match the features
        method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        matcher = cv2.DescriptorMatcher_create(method)
        matches = matcher.match(descsA, descsB, None)

    else:
        # if no IR equivalent to the RGB image
        pass


### END OF ALIGNMENT PLAYING ####



###########################################################################
# TODO: normalise image colors
# TODO: read in temperature "images" as well
# TODO: align / register temperature and color images
# https://www.pyimagesearch.com/2020/08/31/image-alignment-and-registration-with-opencv/
###########################################################################

# tried green_inRange_mask, light_inRange_mask, make_edge_mask
# all ok, none perfect. Think best to wait for real box images to tune.
imgs = make_plant_masks(imgs, make_edge_mask)

imgs, component_stats = get_connected_components(imgs, img_timeseries_order)

###################################################################
# TODO : HERE, could also filter / merge on proximity & filter by
# shape / aspect ratio of component..? (or improve initial masking!)
###################################################################
should_keep = get_component_size_filter(component_stats)

imgs, roi_imgs = segment_images(imgs, component_stats, should_keep)

roi_imgs = resize_rois(roi_imgs, out_width, out_height)


print('saving intermediate stages to :'+out_dir_sanity)
for k in imgs:
    for i in range(len(imgs[k])):
        cv2.imwrite(out_dir_sanity+k+'_'+str(i)+'.jpg', imgs[k][i])


print('saving ROIs to :'+out_dir_ROI)
for id in roi_imgs:
    cv2.imwrite(out_dir_ROI+id+'.jpg', roi_imgs[id])

# # show state of images
# for k, i in imgs.items():
#     show_pics(imgs[k])
