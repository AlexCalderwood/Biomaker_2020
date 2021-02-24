# User interface

# load libraries, data -------------------------------
here::i_am('dashboard/ui.R')
library(here)
library(data.table)

statsPath <- here('plotting_and_stats', 
                  'example_output_model_A')

summary_table <- fread(paste0(statsPath, '/summary_table.csv'))


# page 1 - Summary of results ------------------------
summary_panel <- tabPanel("Summary",
                          titlePanel("Results Summary"),
                          fluidRow(
                            column(12, 
                                   DT::dataTableOutput('summary_table')
                                   )),
                          p(em("*different indicates that a period of different response to the cabinet exists between these groups"))
                          )

# # page 2 - Timeseries graphs -------------------------
sidebar_content <- sidebarPanel(
  selectInput(
    'timeseries_metric',
    label = 'Metric:',
    choices = summary_table$metric),
  tags$p(tags$b('Raw Data:'), 'shows the data extracted from the imaging'),
  tags$p(tags$b('Individual Fit:'), 'shows the fitted function for each individual plant'),
  tags$p(tags$b('Group Fit:'), 'shows the modelled function ±2 s.e. for each plant group'),
  tags$p(tags$b('Group Difference'), 'shows the mean ±2 s.e. for the estimated differences in 
         response between the groups'),
  tags$p("Changes in the metrics over time were modelled as hierarchical spline models. So the value for each 
  individual plant is modelled as the sum of the effect of the group it's in, and it's deviation
  from the group."),
  tags$p("Coefficients are estimated using ", tags$em("fREML (fast Resticted Maximum Likelihood)"),
         'using the ', tags$em('mgcv'), ' package in R.'),
  tags$p("Hierarchical models can be unstable due to the inherantly correlated coefficients - be sure to
  check that the divergence of individual plants from the group means are not overfitting, and 
         compensating for a poorly modelled group effect!")
  )

main_content <- mainPanel(
  fluidRow(column(width=6, tags$h3('Raw Data', style='text-align:center;'), 
                  imageOutput('data_plot', height='100%')), 
           column(width=6, tags$h3('Individual Fit', style='text-align:center;'), 
                  imageOutput('plant_fit_plot',  height='100%'))),
  fluidRow(column(width=6, tags$h3('Group Fit', style='text-align:center;'), 
                  imageOutput('group_fit_plot',  height='100%')),
           column(width=6, tags$h3('Group Difference', style='text-align:center;'), 
                  imageOutput('difference_plot',  height='100%')))
)

timeseries_panel <- tabPanel("Timeseries Results",
                             titlePanel("Timeseries Results"),
                             sidebarLayout(sidebar_content,
                                           main_content)
                             )
                             


# define user interface as combo of above ------------
ui <- navbarPage('Stressful cabinet', 
                 summary_panel,
                 timeseries_panel)
