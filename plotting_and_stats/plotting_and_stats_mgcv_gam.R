rm(list=ls())
here::i_am('plotting_and_stats/plotting_and_stats_mgcv_gam.R')

library(here)
library(data.table)
library(ggplot2)
library(mgcv) # fitting GAM model
set.seed(2567)


translate_by_yintercept <- function(x) {
  return(x - x[1])
}

untranslate_by_yintercept <- function(curr.dt) {
  curr.dt$diff <- curr.dt$value - curr.dt$value.sc
  curr.dt[, grp.diff:=mean(diff), by=.(plant.group, variable)]
  curr.dt$yhat <- curr.dt$sc.yhat + curr.dt$diff
  curr.dt$yhat_group <- curr.dt$sc.yhat_group + curr.dt$grp.diff
  curr.dt$diff <- NULL
  return(curr.dt)
}

make_pairwise_comparisons <- function(groups) {
  # make list of pairwise comparisons possible between the plant groups
  groups <- unique(groups)
  comparisons <- list()
  for (i in 1:length(groups)) {
    for (j in 1:length(groups)) {
      if (j > i) {
        comparisons <- c(comparisons, list(c(as.character(groups[i]), as.character(groups[j]))))
      }
    }
  }
  return(comparisons)
}

make_new_pred_data <- function(data, num_timepoints) {
  # make new pred data with all plants and all groups, from min to max 
  # observed timepoints, with num_timepoints equally distributed sampling times.
  X <- seq(min(data$time.int), 
           max(data$time.int),
           length.out=num_timepoints)
  X.data <- data.table('time.int'=X,
                       'dummy'=1)
  plant.data <- unique(data[, c('plant.group', 'plant.id')])
  plant.data$dummy=1
  pred.data <- merge(X.data, plant.data, by='dummy', allow.cartesian=T)
  pred.data$dummy <- NULL
  return(pred.data)
}

make_group_predictions <- function(curr.mod, curr.dt) {
  # make predictions for mean and se of group level smooths
  # this DOES NOT iclude uncertainty due to the intercept
  
  # get values for all basis functions
  Xp <- predict(curr.mod, newdata=curr.dt, type='lpmatrix')
  
  # zero out all non plant group by time effects (the intercept, and the plant.id by time effects)
  Xp[, !grepl('^s\\(time\\.int):plant\\.groupG', colnames(Xp))] <- 0
  # 0 out all plant id effects, just leaving differences in group intercepts, and differences
  # Xp[, grepl('plant.id', colnames(Xp))] <- 0
  
  
  fit <- Xp %*% coef(curr.mod)
  se <- sqrt(rowSums((Xp %*% vcov(curr.mod, unconditional = F) * Xp)))
  
  # shift to include mean intercept value to make align to the actual data for interpretable plotting 
  # (rather than just showing the smooth values, which is off from the actual data of the group by the intercept).
  # Nb this is only used for plotting, not for any inference of same / different.
  fit <- fit + coef(curr.mod)[1] # all get the intercept, only not first group also get their own
  for (i in 2:length(unique(curr.dt$plant.group))) {
    curr.group <- unique(curr.dt$plant.group)[i]
    fit[curr.dt$plant.group==curr.group] <- fit[curr.dt$plant.group==curr.group] + coef(curr.mod)[i]
  }
  return(list('fit'=fit, 'se'=se))
}

calc_diff_between_groups <- function(model, modelled.data, grp1, grp2) {
  # calculate the expectation and CI for the difference between
  # grp2 interaction with time, and grp2 interaction with time
  
  # model in mgcv::gam() fitted object using 
  # value ~ plant.group + s(time.int, by=plant.group) + s(time.int, plant.id, bs='fs')
  # formula
  
  # curr.dt is the data used to fit it
  # grp1 / grp2 are strings corresponding to the groups being compared 
  # (entries in the plant.group column of modelled.data)
  
  # is there a difference between group:time smooths? (nb NOT intercept)
  # following https://fromthebottomoftheheap.net/2017/10/10/difference-splines-i/
  # matrix of values of basis functions
  
  # make new x data to predict suing model
  # num_pred_timepoints <- 500
  # pred.data <- make_new_pred_data(modelled.data, num_pred_timepoints)
  # X = unique(pred.data$time.int)
  pred.data <- modelled.data

  # get values of the basis functions used to make the predictions
  # only g1 basis functions are non-zero.
  # doesn't matter which indiv plant in each group is picked, as
  # zero out all basis functions which are plant specific lower down.
  # (so doing all plants gives duplicate values for all plants in a group)
  grp1.eg.plant <- pred.data[pred.data$plant.group==grp1, c(plant.id)][1]
  Xp1 <- predict(model, 
                 newdata=pred.data[pred.data$plant.id==grp1.eg.plant,],
                 type='lpmatrix')
  # only g2 basis functions are non-zero
  grp2.eg.plant <- pred.data[pred.data$plant.group==grp2, c(plant.id)][1]
  Xp2 <- predict(model, 
                 newdata=pred.data[pred.data$plant.id==grp2.eg.plant,],
                 type='lpmatrix')
  
  # calc. differences in values of basis functions at each timepoint between grp1 and grp2
  Xdiff <- Xp1 - Xp2
  
  # zero out cols related to other groups (though should all be 0 anyway)
  c1 <- grepl(grp1, colnames(Xdiff))
  c2 <- grepl(grp2, colnames(Xdiff))
  Xdiff[, !(c1 | c2)] <- 0
  
  # zero out cols which are not to do with the interaction
  # between group and time.int 
  # nb here, we include the intercept term, becasue even if
  # data has the same intercept, the splines fit fot the group:time interaction
  # might not, if differnet coefficients. If don't do this, then the location of the differences
  # doesn't work (is off due to difference in the spline intercept).
  Xdiff.fit <- copy(Xdiff)
  Xdiff.fit[, grepl(':plant\\.id', colnames(Xdiff))] <- 0
  # calculate expected different
  dif <- Xdiff.fit %*% coef(model)

  # calculare uncertainty around the estimated difference
  # (this is as in the "from the bottom of the heap" blog, but see
  # also https://stats.stackexchange.com/questions/110091/how-to-calculate-the-robust-standard-error-of-predicted-y-from-a-linear-regressi
  # for the restated fromula, though there takes diagonals, rather than rowSums
  # think difference is because basis are functional rather than scalar?!?). Trust in Gavin Simpson.
  
  # for uncertainty in the difference, only want to incorporate uncertainty due to group:time effect, NOT
  # intercept uncertainty, so use Xdiff.cov (with zero'd intercept), rather than Xdiff.fit (with non-zero intercept) again
  Xdiff.cov <- copy(Xdiff)
  Xdiff.cov[, !grepl('^s\\(time\\.int):plant\\.groupG', colnames(Xdiff))] <- 0
  se <- sqrt(rowSums((Xdiff.cov %*% vcov(curr.mod, unconditional = F) * Xdiff.cov)))
  
  # # calculate 95% interval
  crit <- qt(0.975, df.residual(model)) # qt() is for student t-distribution, with that many dfs
  # (this is basically 1.96)
  upr <- dif + (crit * se)
  lwr <- dif - (crit * se)
  
  diff.df <- data.frame(pair=paste0(grp1, '-', grp2),
              datetime=unique(pred.data$datetime),
              time.int = unique(pred.data$time.int),
              diff=dif,
              se=se, 
              upper=upr,
              lower=lwr)
  return(diff.df)
}

fix_data_formatting <- function(dt) {
  # all the little needed changes format wise to go from 
  # wide table read from csv to data table can fit models with.
  
  dt.m <- melt(dt, id.vars=c('timepoint', 'plant.group', 'plant.id'))
  
  # convert group info to factor (required to work with mgcv)
  dt.m$plant.group <- as.factor(dt.m$plant.group)
  dt.m$plant.id <- as.factor(dt.m$plant.id)
  # convert time as string to datetime
  dt.m[['datetime']] <-  as.POSIXct(dt.m[['timepoint']],
                                    format='%Y-%m-%dT%H-%M-%S',
                                    tz='GMT')
  # use integer rather than datetime
  time.int <- seq(0, 1, length.out=length(unique(dt.m$timepoint)))
  u.times <- unique(dt.m$datetime)
  date2int <- data.frame('time.int'=time.int, 
                         'datetime'=u.times[order(u.times)])
  dt.m <- merge(dt.m, date2int)
  
  return(dt.m)
}

all_include_0 <- function(df) {
  # returns TRUE if CIs for difference between f() don't include 0 for all values,
  # (so think are different). Returns FALSE otherwise (95% CI includes 0 for all values.)
  if (all(df$lower <= 0) & all(df$upper >=0)) {
    return(FALSE)
  } else {
    return(TRUE)
  }
}

make_plots <- function(curr.dt) {
  # make plot of data only
  # plot of data and fit to plants
  p.data <- ggplot(curr.dt, aes(x=datetime, y=value, colour=plant.group, group=plant.id))+
    geom_line(size=0.1)+
    xlab('')+
    ylab('')+
    labs(color='plant group')+
    theme_bw()+
    theme(legend.position='top')
  
  # plot of data and fit to plants
  p.plant.fit <- ggplot(curr.dt, aes(x=datetime, y=value, colour=plant.group, group=plant.id))+
    geom_line(size=0.1)+
    geom_line(aes(y=yhat), size=0.3, alpha=0.6)+
    xlab('')+
    ylab('')+
    labs(color='plant group')+
    theme_bw()+
    theme(legend.position='top')
  
  # data, group pred and se, and where different
  p.grp.fit <- ggplot(curr.dt, aes(x=datetime, y=value, colour=plant.group, group=plant.id))+
    geom_line(size=0.1)+
    geom_line( aes(y=yhat_group, color=plant.group))+
    geom_ribbon(aes(ymin=yhat_group-2*se_group, 
                    ymax=yhat_group+2*se_group, fill=plant.group), color=NA, alpha=0.05)+
    xlab('')+
    ylab('')+
    labs(fill='95% CI for group mean', color='95% CI for group mean')+
    theme_bw()+
    theme(legend.position='top')
  
  # difference plot
  p.grp.diff <- ggplot(diff.dt, aes(x=datetime, y=diff, color=pair, fill=pair))+
    geom_line()+
    geom_ribbon(aes(ymin=lower, ymax=upper), color=NA, alpha=0.3)+
    xlab('*this shows the difference that would exist between groups if they had the same y-value at time 0')+
    ylab('difference in response during experiment')+
    labs(fill='difference between groups (95% CI)', color='difference between groups (95% CI)')+
    theme_bw()+
    theme(legend.title=element_blank(),
          legend.position='top', 
          axis.title.x=element_text(size=6))
  
  return(list(
    'data.plot'=p.data,
    'plant.fit.plot'=p.plant.fit,
    'grp.fit.plot'=p.grp.fit,
    'grp.diff.plot'=p.grp.diff))
}



# SET INPUT AND OUTPUT TO FINAL LOCATIONS
# setup the output directory
outdir <- here::here('plotting_and_stats', 'example_output')

# read the data
dpath <- here::here('plotting_and_stats', 'example_data', 'example_input.csv')
dt <- fread(dpath)
# END OF SETTING INPUT AND OUTPUT - NOTHING ELSE SHOULD NEED CHANGING



# fix the format
dt.m <- fix_data_formatting(dt) 

# bit hacky, but translate each plant to align first timepoint observations
# becasue not interested in differences arising before this. Also seems to help with model convergence.
dt.m[, value.sc:=translate_by_yintercept(value), by=.(plant.id, variable)]

# generate pairwise comparisons between groups
comparisons <- make_pairwise_comparisons(unique(dt.m$plant.group))

all.diff.summary.table <- list()
curr.metric <- 'EG_METRIC_2'

for (curr.metric in unique(dt.m$variable)) {
  print(paste0(curr.metric , '...'))
  
  # crate output directories for current metric
  plt.dir <- file.path(outdir, 'plots', curr.metric)
  dir.create(plt.dir, recursive=T, showWarnings = F)

  # cut data to current metric
  curr.dt <- dt.m[dt.m$variable==curr.metric,]

  # fit hierarchical generalized additive model with plant group and indiv plants within each group
  # use mgcv::bam (rather than mgcv::gam), as optimised for large datasets!!
  # nb  could make even faster with discrete=TRUE
  # if k isn't specified, the default value (10) is used, (it's not fitted)
  # want very diff k for group and plant, to reduce concurvity problem
  # m specifies which derivative is penalised for smoothing penalty - 1 is 1st derivative ie penalises big gradient
  # m=1 will result in smoother curves than m=2 etc.
  # problem with cyclical when very big diff between groups. Think because plant.ids
  # are differently out of sync with the group
  
  # without by, really struggles with very cyclincal. m differences help
  # MODEL_A
  # curr.mod <- mgcv::bam(value.sc ~ plant.group +
  #                         s(time.int, by=plant.group, bs='tp', k=50)+
  #                         s(time.int, plant.id, bs='fs', k=5, m=1),
  #                       data=curr.dt,
  #                       method='fREML')
  
  # having fully seperate by=plant.id seems to make way too confident about group mean value - get false positive
  # differences...
  # MODEL_B
  # curr.mod <- mgcv::bam(value.sc ~ plant.group +
  #                         s(time.int, by=plant.group, bs='tp', k=50)+
  #                         s(time.int, by=plant.id, bs='fs', k=5, m=1),
  #                       data=curr.dt,
  #                       method='fREML')
  
  # MODEL_C
  curr.mod <- mgcv::bam(value.sc ~ plant.group +
                          s(time.int, by=plant.group, bs='tp', k=50)+
                          s(time.int, plant.id, bs='fs', k=5),
                        data=curr.dt,
                        method='fREML')
  
  
  # TODO: depending on how the real data looks, can implement model selection through e.g. 
  # https://stats.stackexchange.com/questions/325832/gam-mgcv-aic-vs-deviance-explained
  # or some other principled approach.!
  
  # TODO: depending on how the real data looks, might have to modify the plotting - e.g. 
  # diff plot isn't zeros in the by=plant.id models
  
  
  
  # mgcv::vis.gam(curr.mod, se=T, theta=120)
  # plot(curr.mod)
  # mgcv::gam.check(curr.mod)
  
  # make predictions at plant level
  p.plant <- predict(curr.mod, newdata=curr.dt, se=T)
  curr.dt$sc.yhat <- p.plant$fit
  curr.dt$se <- p.plant$se
  
  # make predictions for group level smooth
  #plt.grp.dt <- data.table(gratia::evaluate_smooth(curr.mod, "s(time.int)"))
  p.group <- make_group_predictions(curr.mod, curr.dt)
  curr.dt$sc.yhat_group <- p.group$fit
  curr.dt$se_group <- p.group$se
  
  # make predictions for differences between groups
  diffs.list <- list()
  for (c in comparisons) {
    d.df <- calc_diff_between_groups(curr.mod, curr.dt, c[1], c[2])
    diffs.list <- c(diffs.list, list(d.df))
  }
  diff.dt <- data.table(do.call('rbind', diffs.list))
    

  # summarise between group differences as sufficient evidence that
  # statistically different (TRUE), or not (FALSE)
  diff.summary <- data.table(diff.dt[, all_include_0(.SD), by=.(pair)])
  names(diff.summary) <- c('comparison', 'is.different')
  diff.summary$metric <- curr.metric
  all.diff.summary.table <- c(all.diff.summary.table, list(diff.summary))
  
  # translate predictions by yintercepts
  curr.dt <- untranslate_by_yintercept(curr.dt)
  
  # make plots
  curr.plots <- make_plots(curr.dt)
  
  ggsave(paste0(plt.dir, '/data.plot.pdf'), plot=curr.plots[['data.plot']], width=5, height=5)
  ggsave(paste0(plt.dir, '/plant.fit.plot.pdf'), plot=curr.plots[['plant.fit.plot']], width=5, height=5)
  ggsave(paste0(plt.dir, '/grp.fit.plot.pdf'), plot=curr.plots[['grp.fit.plot']], width=5, height=5)
  ggsave(paste0(plt.dir, '/grp.diff.plot.pdf'), plot=curr.plots[['grp.diff.plot']], width=5, height=5)
}

# make aggregate table summarising statistically same / different responses
# in metrics betwen groups
diff.summary.table <- data.table(do.call('rbind', all.diff.summary.table))
diff.summary.table <- dcast(diff.summary.table, 
                            formula = metric ~ comparison, 
                            value.var='is.different')
fwrite(diff.summary.table, 
       file=paste0(outdir, '/summary_table.csv'))

