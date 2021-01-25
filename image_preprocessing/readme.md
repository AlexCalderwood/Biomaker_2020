# pre-processing readme

## DONE:
- image segmentation (good enough until have real box pictures)
- assign consistent plant ids over time-series of same camerafield

## TODOs:
- finalise plant identification /masking parameters
- finalise segment size parameters
- finalise resizing (for input to araDEEPopsis) parameters

- thermal / colour image registration.
- colour normalisation
- (?thermal normalisation?)
- calculate size / scale of pixels in final image

## final input:
- directory of color images, named as "cameraField_YYYY-MM-DDTHH-MM-SS.JPG"
- directory of thermal images, named as "cameraField_YYYY-MM-DDTHH-MM-SS.XXFORMATXX"

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
