# dashboard readme

Launch R Shiny app showing expt results by running **app.R**, either from RStudio,
or directly from command line as
`Rscript app.R`

Annoyingly, requires that all assets are within "www" directory. So need to make
sure that output of statistics pipeline, and image segmentation (and anything else
  want to show through Shiny app) get saved there.

## final input:
- ~~plots & table produced from plotting_and_stats~~ done!
- ~~images showing the steps of the segmentation~~ done!
- ~~segmented images (ROIs)~~ done!
- images showing masks, and convex hull found by aradeepopsis - Still to do!

## jobs:
- pull all into shinyR framework for convenient browsing and debugging of experiment

## final output:
- launch shinyR application showing expt results.
