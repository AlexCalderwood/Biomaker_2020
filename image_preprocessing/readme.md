# pre-processing readme

## DONE:
- image segmentation (good enough until have real box pictures)
- assign consistent plant ids over time-series of same camerafield

## TODOs:
- finalise plant identification /masking parameters - (plantcv documentation
might have some more ideas for masking approaches if can't get one of these
working well)
- finalise segment size parameters
- finalise resizing (for input to araDEEPopsis) parameters

- thermal / colour image registration.
- colour normalisation
- (?thermal normalisation?)
- calculate size / scale of pixels in final image

## final input:
- single directory of RGB & IR images
- named as "<prefix>_YYYY-MM-DDTHH-MM-SS.JPG", where timestamp is time image is taken.

- underscore is used to split timestamp from prefix, so DON'T use them in the prefix!
- timestamp format must be as shown above

- IR image prefix expected to start with "IR"
- RGB image prefix expected to start with "RGB"
- expecting to see each timestamp twice - one for RGB image, one for IR image


## final jobs:
- calculate pixel size (because e.g. evaporative flux calculation needs to know leaf sizes)

- color normalisation: expect to run under different lighting conditions. Need to normalise this for colourmetrics stuff to be comparible between experiments.

- thermal normalisation? : do different lighting setups effect this too?

- image segmentation: AraDEEPopsis expects single plant images.
Also need to assign consistent Plant id to each plant in images over time.

- resizing: AraDEEPopsis expects consistent size images (60 x 60??)

- alignment / registration of color and thermal images: colour is high resolution, and want to use for plant masking, thermal is low resolution.


## final output:
- colour ROIs directory containing segmented (& normalised etc images), for use in next step of pipeline. Files named as "cameraField_YYYY-MM-DDTHH-MM-SS_ID.JPG"
- thermal ROIs directory containing segmented, aligned etc thermal images. Files named as "cameraField_YYYY-MM-DDTHH-MM-SS_ID.JPG"
- intermediate directory showing image state at each step of processing (for sanity / debugging).
- some record of size of pixels in each output ROI.
