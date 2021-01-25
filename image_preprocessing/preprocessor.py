#!/usr/bin/env python
from preprocessor_functions import *

# path to directory containg images to process
in_dir = '/Users/calderwa/projects/biomaker/data/\
Example Arabidopsis rosette images/plate_images/'
out_dir_ROI = '/Users/calderwa/projects/biomaker/data/preprocessed_images/ROIs/'
out_dir_sanity = '/Users/calderwa/projects/biomaker/data/preprocessed_images/\
intermediate/'

out_width = 500  # px width of output segmented imgs
out_height = 500

setup_dirs([in_dir, out_dir_sanity, out_dir_ROI])

imgs = read_images(in_dir)
img_timeseries_order = get_image_order(in_dir)

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
        cv2.imwrite(out_dir_sanity+k+'_'+str(i), imgs[k][i])


print('saving ROIs to :'+out_dir_ROI)
for id in roi_imgs:
    cv2.imwrite(out_dir_ROI+id+'.JPG', roi_imgs[id])

# # show state of images
# for k, i in imgs.items():
#     show_pics(imgs[k])
