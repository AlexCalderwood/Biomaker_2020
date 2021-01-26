# plotting and statistics on output

## final input
Munged data table of araDEEPopsis colourmetrics, as well as any other metrics of interest (other color metrics, thermal metrics, any derived wavelength metrics etc).

As data table with columns of:
timepoint, plant id, plant group, METRICS...

where:
- timepoint is datetime image was taken formated as YYYY-MM-ddTHH-mm-ss. Assume all plants images at the same timepoints.
- plant id is integer id of plant (unique within expt)
- plant group is group plant is in for statistical comparison (e.g. genotype, old/young plant etc). Assume may be 1, 2, more groups in the data.
- metrics uniquely id each.

## final jobs
stats:
- Scale metric for each plant so that for timepoint 1, all values are the same for all plants
- Apply statistical test to identify whether each metric differs between groups across whole timeseries.
- Apply statistical test to identify when each metric differs between groups.

plotting:
- Make table showing metric name, and groups differ between if any
- Make plots showing data over time, fitted confidence intervals, and highlight timepoints where metric is same / different between groups.

## final output
- save table & plots to file, for import into final results dashboard.
