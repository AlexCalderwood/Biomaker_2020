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
                             

# page 3 : show image analysis used in data generation ----------------------

sidebar_content <- wellPanel(
  fluidRow(selectInput(
    'images_metric',
    label = 'Metric:',
    choices = summary_table$metric)),
  fluidRow(tags$p("To view the image processing used in generating any weird looking points, select the region
         of interest with the left hand plot, and click the point(s) in the right hand plot. Images relevant 
                  to that point will display below."))
)

main_content <- fluidPage(
  fluidRow(
    # plot for selecting zoom region
    column(width=6,
           tags$h3('Select region of interest', style='text-align:center;'),
           plotOutput('imgSelectDataPlot',
                      brush = brushOpts(
                        id='dPlot_brush',
                        resetOnNew=T))),
    # plot for selecting points
    column(width=6,
           tags$h3('Select point of interest', style='text-align:center;'),
            plotOutput('imgZoomDataPlot',
                       click='zoomPlotClick',
                       brush=brushOpts(
                         id='zoomPlotBrush'
                       )))),
  # table about selected point
  fluidRow(column(width=6, offset=6, align='center',
                  tableOutput('clickInfo'))),
  
  # show preprocessing images relevant to selected point
  fluidRow(tags$h3(textOutput('testWarning'), style='text-align:center; color:red;')),
  fluidRow(
    tags$h3('Selected point preprocessing images:'),
    column(width=3, 
           tags$h4('Original Image', style='text-align:center;'), 
           imageOutput('origImg', height='100%'),
           tags$h4(textOutput('origImgPath'), style='font-size: 5px;')),
    column(width=3,
           tags$h4('Plant Mask', style='text-align:center;'), 
           imageOutput('maskImg', height='100%'),
           tags$h4(textOutput('maskImgPath'), style='font-size: 5px;')),
    column(width=3,
           tags$h4('Plant Boxes', style='text-align:center;'), 
           imageOutput('boxImg', height='100%'),
           tags$h4(textOutput('boxImgPath'), style='font-size: 5px;')),
    column(width=3,
           tags$h4('Plant Image', style='text-align:center;'), 
           imageOutput('ROIImg', height='100%'),
           tags$h4(textOutput('ROIImgPath'), style='font-size: 5px;'))
    
  )
)



images_panel <- tabPanel('Image Checking',
                         titlePanel('Image Checking'),
                         sidebar_content,
                         main_content)
                         #sidebarLayout(sidebar_content,
                         #              main_content))

# define user interface as combo of above ------------
ui <- navbarPage('Stressful cabinet', 
                 summary_panel,
                 timeseries_panel,
                 images_panel)
