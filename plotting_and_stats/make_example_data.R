rm(list=ls())
here::i_am('plotting_and_stats/make_example_data.R') # declare location of current script relative to project root dir
library(here)
library(data.table)
library(ggplot2)

linear <- function(x, m, c) {
  y = (m * x) + c
  return(y)
}

sigmoid <- function(x, m, k) {
  y = m / (1 + exp((-k * x)))
  return(y)
}

tanh <- function(x, m, c, k) { 
  y = (exp(x)-exp(-m*x)) / (exp(c*x) + exp(-k*x))
  return(y)
}


# make example data in the expected format of
# wide format
# timepoint: 'YYYY-MM-DDThh-mm-ss' format
# plant_id: integer id unique to each plant
# plant_group: string identifying group plant is in. Statistics will make comparisons
# between groups.
# EG_METRIC_1, 2, 3, etc.

# make timepoints
start = as.POSIXct('2021-09-02 09:00:00')
start
times = start + seq(0, 2879*60, 2*60) # simulate sample every 2 minutes for 2 days
times_str = strftime(times, format='%Y-%m-%dT%H-%M-%S')

grpsize = 7 # number of plants in each group
groups = c('G1', 'G2', 'G3') # ids of the different groups


# generate some timeseries. Want some periodic, some monotonic, some whatever,
# and some combinations of these.
# want each group to be same, with some noise between plants
# want not all plants to start at the same value

set.seed(5)
datalist= list()
x = seq(0, 1, length.out = length(times))
for (gi in 1:length(unique(groups))) {

  # set group paramater values
  # linear
  mg = runif(1, min= 1, max=5)
  cg = runif(1, min = 0.1, max=5)
  # sin
  kg = runif(1, min = 0.05, max = 0.15)
  # sigmoid
  maxg = runif(1, min=1, max=5)
  lg = runif(1, min=6, max=20)
  # tanh - reusing others gives fine resutls

  for (pi in 1:grpsize) {
    pID = ((gi-1) * grpsize) + pi
    
    # set plant parameter values as group + some gaussian noise
    # linear
    mp = mg + rnorm(1, mean = 0, sd = 0.3)
    cp = cg + rnorm(1, mean = 0, sd = 0.1)
    # sin
    kp = kg + rnorm(1, mean = 0, sd = 0.005)
    # sigmoid
    maxp = maxg + rnorm(1, mean=0, sd=0.15)
    lp = lg + rnorm(1, mean=0, sd=0.5)
    # tanh
    
    # calculate some function values for each plant, with observational noise
    yLin = linear(x, mp, cp) + rnorm(length(x), mean=0, sd = 0.01)
    ySin = sin(x / kp) + rnorm(length(x), mean=0, sd = 0.05)
    ySig = sigmoid(x, maxp, lp) + rnorm(length(x), mean=0, sd = 0.01)
    yTanh = tanh(x, mp, cp, kp) + rnorm(length(x), mean=0, sd=0.001)
    
    p.df = data.table(data.frame('timepoint'=times_str, 
                                 'plant group'=groups[gi], 
                                 'plant id'=pID,
                                 'EG_METRIC_1'=yLin,
                                 'EG_METRIC_2'=ySin,
                                 'EG_METRIC_3'=ySig,
                                 'EG_METRIC_4'=yTanh,
                                 'EG_METRIC_5'=yLin+ySin,
                                 'EG_METRIC_6'=5*yTanh + 0.2*(yLin+ySin)
                                ))
    datalist = c(datalist, list(p.df))
  }
}
dt = do.call('rbind', datalist)


# test plotting
dt.m = melt(dt, id.vars=c('timepoint', 'plant.group', 'plant.id'))
p <- ggplot(dt.m, aes(x=timepoint, y=value, color=plant.group, group=plant.id))+
  facet_wrap(~variable, scales='free')+
  geom_line(alpha=0.7)+
  theme(
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank(),
    legend.position = 'top'
  )

# save plot and csv of dummy data
ggsave(
  here::here('plotting_and_stats', 'example_data', 'example_input_plot.pdf'),
  width=7, height=5
)
fwrite(dt, 
       file=here::here('plotting_and_stats', 'example_data', 'example_input.csv'))
  