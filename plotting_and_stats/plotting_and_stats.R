rm(list=ls())
here::i_am('plotting_and_stats/plotting_and_stats.R')

library(here)
library(data.table)
library(ggplot2)
library(splines)
library(rstan)


scale_by_first_obs <- function(x) {
  return(x / x[1])
}


# read the data & convert to long format
dpath <- here::here('plotting_and_stats', 'example_data', 'example_input.csv')
dt <- fread(dpath)
dt.m <- melt(dt, id.vars=c('timepoint', 'plant.group', 'plant.id'))

# convert time as string to datetime
dt.m[['datetime']] <-  as.POSIXct(dt.m[['timepoint']], 
                                  format='%Y-%m-%dT%H-%M-%S',
                                  tz='GMT')

# scale each observed metric for each plant, so first observation for each plant is "1",
# to avoid issues if plants different sizes at start, but response is the same once in box.
dt.m <- dt.m[order(timepoint)]
dt.m[, scaled.value:=scale_by_first_obs(value), by=.(plant.id, variable)]



### FITTING B-SPLINE MODELS TO THE DATA:

### Preparing the data
num_plants <- length(unique(dt.m$plant.id))

# generate a numerical values for X axis
num_obs <-  length(unique(dt.m$timepoint)) # number of timepoints observed
X <-  seq(0, 1, length.out=num_obs)

# generate basis splines
num_knots <-   10 # number of knots to use in B-splines
B <-  t(bs(X, 
         knots=seq(min(X), max(X), length.out=num_knots), 
         degree=3, 
         intercept = TRUE)) # B-spline values over X
num_basis <- nrow(B)

num_groups <- length(unique(dt.m$plant.group))
# generate group one-hot encoding of plants - no longer persuing stan model which needed this
# G <- dcast(unique(dt.m[, c('plant.id', 'plant.group')]), 
#            plant.id ~ plant.group, 
#            value.var='plant.group')
# G <- G[, -1]
# G[!(is.na(G))] <- 1
# G[is.na(G)] <- 0 # rows are plant.id

# convert group labels to group id integers for use as indices in stan model
G <- unique(dt.m[, c('plant.id', 'plant.group')])
G <- G[order(plant.id)]
G$plant.group <- as.factor(G$plant.group)
G$plant.group.idx <- as.integer(G$plant.group)
G.idx <- G$plant.group.idx # vector of the index of the group each plant is in.


# FOR EACH METRIC

# get Y values in num_plants x num_obs matrix
curr_variable <-  'EG_METRIC_1'
obs <-  dt.m[variable==curr_variable, c('plant.id', 'variable', 'value', 'datetime')]
obs.c <- dcast(obs, datetime ~ plant.id)
obs.c <- obs.c[order(obs.c$datetime),]
Y <- as.matrix(obs.c[, -1])
Y <- t(Y)

stan_data <- list(num_plants=num_plants,
                  num_groups=num_groups,
                  num_obs=num_obs,
                  num_basis=num_basis,
                  Y=Y,
                  X=X,
                  B=B,
                  G=G.idx)

stan_file <- here::here('plotting_and_stats', 'B-spline_model.stan')

rstan_options(auto_write = TRUE) # compiled instance of stanmodel-class is written to HD in same directory as .stan program
options(mc.cores = parallel::detectCores()) # detect cores available
fit <- stan(file=stan_file,
            data=stan_data, 
            warmup=500,
            iter=1000, chains=1)
posterior <- extract(fit) # put posterior estimates for each param into a list.

