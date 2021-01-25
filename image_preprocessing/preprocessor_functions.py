import cv2
import numpy as np
import os
from datetime import datetime

def setup_dirs(dirList):
    for d in dirList:
        if not os.path.exists(d):
            os.makedirs(d)


def read_images(inDir):
    # return dict of {filename: [openCV image object]}

    files = os.listdir(inDir)
    # ignore hidden files
    files = [f for f in os.listdir(inDir) if not f.startswith('.')]
    images = {}

    for i, f in enumerate(files):
        print(f)
        path = inDir + f
        # print(path)
        images[f] = [cv2.imread(path)]

    return images


def filename_to_timestamp(fName):
    '''
    Assumes fName is SOMEPREFIX_TIMESTAMP.xxx
    where TIMESTAMP is YYYY-mm-ddTHH-MM-SS
    '''
    f_strip = fName.split('.')[0]
    time_str = f_strip.split('_')[1]
    date = datetime.strptime(time_str, '%Y-%m-%dT%H-%M-%S')

    return date


def get_image_order(inDir):
    '''
    read the filenames in inDir, and return dict with order images taken in
    for each PREFIX.

    assumes filenames are PREFIX_TIMESTAMP.xxx format

    where PREFIX identifies camera view
    where TIMESTAMP is YYYY-mm-ddTHH-MM-SS

    returns dict of {prefix : [filenames with prefix in time order]}
    '''

    # ignore hidden files
    files = [f for f in os.listdir(inDir) if not f.startswith('.')]
    sorted_files = {}

    prefixes = set([f.split('_')[0] for f in files])
    for p in prefixes:
        curr_files = []
        for f in files:
            if p in f:
                curr_files.append(f)

            sorted_curr_files = sorted(curr_files, key=filename_to_timestamp)
            sorted_files[p] = sorted_curr_files

    return sorted_files


def show_pics(images):
    """
    quick testing function to show the state of images.
    shows all pictures. Closes and continues on keystroke.
    images : list of openCV image objects
    """

    width = 800
    for i, img in enumerate(images):
        tmp = img.copy()
        w = tmp.shape[1]
        h = tmp.shape[0]
        aspect = w / h

        height = int(width / aspect)

        tmp = cv2.resize(tmp, (width, height))  # rescale to 200 x 200 px
        cv2.imshow('image_'+str(i), tmp)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return


def make_light_inRange_mask(img):
    # rather than look for plants, look for grey background
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    # apply blur helps with avging lightness
    hls_b = cv2.blur = cv2.GaussianBlur(hls, (11, 11), 0)

    # define "light" range format is (hue, lightness, saturation)
    lower_light = np.array([0, 100, 0])
    upper_light = np.array([255, 255, 255])
    mask = cv2.inRange(hls_b, lower_light, upper_light)
    inv_mask = cv2.bitwise_not(mask)

    # blurring a bit helps connected components finding
    inv_mask_b = cv2.GaussianBlur(inv_mask, (31, 31), 0)
    inv_mask_b[inv_mask_b > 0] = 255

    mask_sanity = cv2.bitwise_and(img, img, mask=inv_mask_b)

    return [inv_mask_b, mask_sanity]


def make_green_inRange_mask(img):
    # convert to HSV format
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # apply blur
    hsv_b = cv2.blur = cv2.GaussianBlur(hsv, (11, 11), 0)

    # define "green" range
    lower_green = np.array([40, 40, 50])
    upper_green = np.array([100, 255, 255])
    mask = cv2.inRange(hsv_b, lower_green, upper_green)

    mask_sanity = cv2.bitwise_and(img, img, mask=mask)

    return [mask, mask_sanity]


def make_edge_mask(img):
    '''playing with edge detection for mask'''

    # show_pics([img])
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # edge detection
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edges = cv2.Canny(blurred, 40, 100)
    #show_pics([edges])

    # broaden edges - make contiguous lines
    thick_edges = cv2.GaussianBlur(edges, (15, 15), 0)
    thick_edges[thick_edges > 0] = 255
    #show_pics([thick_edges])

    # # convert edges to contours - just use edges!
    # _, contours, _ = cv2.findContours(thick_edges,
    #                                   cv2.RETR_EXTERNAL,
    #                                   cv2.CHAIN_APPROX_SIMPLE)
    #
    # # mask = cv2.fillPoly(thick_edges, contours, color = (255))
    # mask = cv2.drawContours(thick_edges, contours, -1,
    #                         color=(255), thickness=10)

    mask = thick_edges
    mask_sanity = cv2.bitwise_and(img, img, mask=mask)

    return [mask, mask_sanity]


def make_plant_masks(imgs, mask_fun):
    """
    applies "mask_fun" to first element of imgs dict.
    returns {fileName : [orig-image, mask, mask-image-overlay]}
    """
    for key, val in imgs.items():
        imgs[key].extend(mask_fun(val[0]))

    return imgs


def get_component_size_filter(stats_dict):
    '''
    filter connected components based on area, width and height to
    cut down on individual leaves, ruler, etc being flagged.

    stats: matrix of stats. Columns are
    0 : cv2.CC_STAT_LEFT
    1 : cv2.CC_STAT_TOP
    2 : cv2.CC_STAT_WIDTH
    3 : cv2.CC_STAT_HEIGHT
    4 : cv2.CC_STAT_AREA
    https://stackoverflow.com/questions/35854197/how-to-use-opencvs-connected-components-with-stats-in-python

    returns dict of {filename: keep vector of True / False}
    '''

    print('filtering connected components based on size')

    min_width = 200
    max_width = 1000
    min_height = 200
    max_height = 1000
    min_area = 10000
    max_area = 200000

    should_keep_dict = {}

    # iterate over images
    for key in stats_dict:
        n_labels = stats_dict[key]['n_labels']
        stats = stats_dict[key]['stats']

        should_keep = [False] * n_labels

        # iterate over components
        for i in range(n_labels):
            if min_width < stats[i, 2] < max_width and \
             min_height < stats[i, 3] < max_height and \
             min_area < stats[i, 4] < max_area:

                should_keep[i] = True

        should_keep_dict[key] = should_keep

    return should_keep_dict


def get_connected_components(imgs, key_order):
    '''
    takes imgs dict of lists with mask at [1] position for each entry,
    and uses to get connected components (which should be individual plants).

    checks found same number of connected components in each img_timeseries

    ensures consistent labelling of plants in all images of timeseries.

    ***input***:
    imgs: dict of images with mask in [1] position for each
    key_order: dict of timeseries order for each image set

    ***returns***:
    appends false colour image of components to imgs.

    returns dict of {filename: {'n_labels': number of components,
                                'labels': group id number of each pixel in img,
                                'centroids': matrix of xy coords of centroids
                                (row is group id),
                                'stats: openCV connected component stats.'}}
    '''
    out = {}

    for prefix in key_order:
        for i, filename in enumerate(key_order[prefix]):
            mask = imgs[filename][1]

            n_labels, labels, stats, centroids =\
             cv2.connectedComponentsWithStats(mask, connectivity=8)

            # if first img in current timeseries, generate colors
            if (i == 0):
                start_n_labels = n_labels
                start_centroids = centroids
                colors = np.random.randint(0, 255, size=(n_labels, 3),
                                           dtype=np.uint8)
                colors[0] = [0, 0, 0]  # set background to black

            # if not the first img in the timeseries, set consistent labels
            # to first image, based on nearest centroid
            else:
                # check found the same number of continuous objects (plants)
                assert start_n_labels == n_labels, 'Inconsistent number of \
                plants found for ' + prefix

                # map the labels to the labels found in the first img in
                # timeseries
                label_lookup = get_closest_objects(centroids, start_centroids)

                # rename labels
                labels, centroids, stats = \
                 relabel_stats(label_lookup, labels, centroids, stats)

            # add colored connected components image
            false_colors = colors[labels]
            imgs[filename].append(false_colors)

            # add the stats to out dictionary
            out[filename] = {'n_labels': n_labels,
                             'labels': labels,
                             'centroids': centroids,
                             'stats': stats
                             }

    return imgs, out


def relabel_stats(label_lookup, labels, centroids, stats):
    # vectorised with mapping array - loop is V. slow!
    # https://stackoverflow.com/questions/55949809/efficiently-replace-elements-in-array-based-on-dictionary-numpy-python
    k = np.array(list(label_lookup.keys()))
    v = np.array(list(label_lookup.values()))
    mapping_ar = np.zeros(k.max()+1, dtype=v.dtype)
    mapping_ar[k] = v

    fixed_labels = mapping_ar[labels]
    fixed_centroids = centroids[mapping_ar, :]
    fixed_stats = stats[mapping_ar, :]

    return fixed_labels, fixed_centroids, fixed_stats


def distance(p, q):
    '''calc square distance between 2d p and 2d q'''
    assert len(p) == len(q)
    return (p[0] - q[0])**2 + (p[1] - q[1])**2


def get_closest_objects(xy1, xy_ref):
    '''
    return dict of which row in xy1 nearest which row xy_ref
    {xy1 row : nearest xy_ref row}
    '''
    out = {}
    for i in range(xy1.shape[0]):
        test = xy1[i, :]
        ds = []
        for j in range(xy_ref.shape[0]):
            ref = xy_ref[j, :]
            ds.append(distance(test, ref))
        out[i] = ds.index(min(ds))

    return out


def segment_images(img_dict, stats_dict, should_keep_dict):
    '''
    get ROIs around the centroid for each components

    update the false colour img to show segs extracted

    return the segements as {origFilename_components_ID: ROI}
    '''

    roi_dict = {}

    segment_width = 650  # for now, hardcode pixels for width and height of ROIs
                         # if variable, then getting plant size from resized
                         # images will be a pain...
                         # could in future use stats which has left, top, out_width
                         # height info of connected component.
    segment_height = 650

    # iterate over images
    for key in img_dict:
        should_keep = should_keep_dict[key]

        # iterage over centroids
        num_connected_components = stats_dict[key]['centroids'].shape[0]
        for plant_idx in range(num_connected_components):
            centroid = stats_dict[key]['centroids'][plant_idx, :]
            num_rows = img_dict[key][0].shape[0]
            num_columns = img_dict[key][0].shape[1]

            t, r, b, l = get_bounds(centroid, segment_width, segment_height,
                                    num_rows, num_columns)

            # annotate imgs with where the ROI is
            if should_keep[plant_idx]:
                color = (0, 255, 0)  # green
            else:
                color = (0, 0, 255)  # red

            img_dict[key][3] = cv2.rectangle(img_dict[key][3],
                                             (l, t),
                                             (r, b),
                                             color,
                                             10)

            # get regions of interest
            if should_keep[plant_idx]:
                roi = img_dict[key][0][t:b, l:r]
                img_file = key.split('.')[0]
                roi_dict[img_file+'_P'+str(plant_idx)] = roi

    return img_dict, roi_dict


def get_bounds(c, w, h, max_y, max_x):
    '''
    returns top, right, bottom, left, pixels of square of size "size",
    centred on "c"

    openCV images are indexed from top left corner
    '''
    x, y = int(c[0]), int(c[1])

    top = max([(y - int(h / 2)), 0])
    right = min([(x + int(w / 2)), max_x])
    bottom = min([(y + int(h / 2)), max_y])
    left = max([(x - int(w / 2)), 0])

    return top, right, bottom, left


def resize_rois(imgs, w, h):
    '''
    resize regions of interest so correct shape for downstream analysis
    '''

    print('resizing ROIs to %i x %i ' % (w, h))

    for k in imgs:
        imgs[k] = cv2.resize(imgs[k], (w, h))

    return imgs
