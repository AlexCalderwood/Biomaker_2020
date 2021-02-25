# load libraries, data ------------------------------------
here::i_am('dashboard/server.R')
library(here)
library(data.table)
library(stringr)
library(DT) # R interface to JavaScript "DataTables" libarary
library(ggplot2)

# path to stats summary
statsPath <- paste0('www/example_stats_output')
# path to statistics timeseries plot
plotPath <- paste0(statsPath, '/plots/')
# path to preprocessing images
imgPath <- paste0('www/example_preprocessing_output')
intImgPath <- paste0(imgPath, '/intermediate/')
ROIPath <- paste0(imgPath, '/ROIs/')


red = '#D22D5C'
green = '#2CD16B'

# server ---------------------------------------------------

server <- function(input, output, session) {

  # page 1: summary results table ------------------------------------------
  # format table content
  
  summary_table <- fread(paste0(statsPath, '/summary_table.csv'))
  names(summary_table) <- str_replace(names(summary_table), 
                                      pattern='-', 
                                      replacement=' vs ')
  summary_table[summary_table==TRUE] <- 'different'
  summary_table[summary_table==FALSE] <- 'same'
  
  # control table styling
  output$summary_table <- DT::renderDataTable(
    {
      datatable(summary_table,
               rownames=F,
               options=list(
                 columnDefs=list(list(className='dt-center', targets='_all')))
               ) %>% 
      DT::formatStyle(2:ncol(summary_table),
                  backgroundColor=DT::styleEqual(c('different', 'same'), c(red, green)))
    })
  
  # page 2: timeseries plots -------------------------------------------------
  # for quick convenience, just open as image. Want eventually to be able to 
  # at least open as object, so dynamic sizing works etc.

  # render the timeseries plots. Use renderImage, as
  # renderPlot is pretty slow.
  output$data_plot <- renderImage(
    {
     path <- paste0(plotPath, '/', input$timeseries_metric, '/plant.fit.plot.png')
     # use w for width and height, as height doesn't change, 
     # and are the same anyway
     w <- session$clientData$output_data_plot_width 
     #readRDS(data_plot_path())
      list(src=path,
           width=w,
           height=w)
    }, deleteFile=F
  )
  output$plant_fit_plot <- renderImage(
    {
      path <- paste0(plotPath, '/', input$timeseries_metric, '/plant.fit.plot.png')
      w <- session$clientData$output_data_plot_width 
      #readRDS(plant_fit_plot_path())
      list(src=path,
           width=w,
           height=w)
    }, deleteFile=F
  )
  output$group_fit_plot <- renderImage(
    {
      path <- paste0(plotPath, '/', input$timeseries_metric, '/grp.fit.plot.png')
      w <- session$clientData$output_data_plot_width 
      #readRDS(group_fit_plot_path())
      list(src=path,
           width=w,
           height=w)
    }, deleteFile=F
  )
  output$difference_plot <- renderImage(
    {
      path <- paste0(plotPath, '/', input$timeseries_metric, '/grp.diff.plot.png')
      w <- session$clientData$output_data_plot_width 
      #readRDS(difference_plot_path())
      list(src=path,
           width=w,
           height=w)
    }, deleteFile=F
  )
  
  # Page 3: image analysis ------------------------------------------
  
  #### interactive plots -------------------
  # used to highlight point of interest
  
  # track region to zoom in on.
  ranges <- reactiveValues(x=NULL, y=NULL, showPoints=FALSE)
  # zoom to brush bounds + add points, otherwise, reset zoom
  # and remove points
  observe({
    print('updating ranges based on brush')
    brush <- input$dPlot_brush
    if (!is.null(brush)) {
      ranges$x <- c(as.POSIXct(brush$xmin, origin='1970-01-01'), 
                    as.POSIXct(brush$xmax, origin='1970-01-01'))
      ranges$y <- c(brush$ymin, 
                    brush$ymax)
      ranges$showPoints <- TRUE
    } else {
      ranges$x <- NULL
      ranges$y <- NULL
      ranges$showPoints <- FALSE
    }
  })
  
  # track point nearest click event
  nearestPoint <- reactiveValues(d=NULL,
                                 rawPath=NULL,
                                 maskPath=NULL,
                                 boxPath=NULL,
                                 ROIPath=NULL,
                                 isTest=TRUE) # if isTest, substitute dummy files
  
  observe({
    clickPoint <- input$zoomPlotClick
    if (!is.null(clickPoint)) { # need to not change value if not clicked, otherwise keeps changing to null value 
      # after input$zoomPlotClick, which triggers plot re-rendering.
      
      # update with table of info about the nearest point
      nearestPoint$d <- nearPoints(data(), clickPoint, maxpoints=1)
      
      # update the paths to the associated preprocessing image files
      # time string used for file names
      t <- as.character(nearestPoint$d$datetime)
      t <- str_replace(t, ' ', 'T')
      t <- str_replace_all(t, ':', '-')
      # get plant id used in naming files
      plant_id <- as.character(nearestPoint$d$plant.id)
      
      # grep the intermediate images files
      if (!(nearestPoint$isTest)) {
        match_files <- list.files(path=intImgPath, pattern=t)
      } else {
        print('TESTING!: substituting dummy images!')
        pat <- sample(c('2020-12-21T11-16-49', '2020-12-21T11-17-49', '2020-12-21T11-18-49','2020-12-21T11-19-49'), 1)
        match_files <- list.files(path=intImgPath, pattern=pat)
      }
      nearestPoint$rawPath <- paste0(intImgPath, match_files[grep('_0', match_files)])
      nearestPoint$maskPath <- paste0(intImgPath, match_files[grep('_1', match_files)])
      nearestPoint$boxPath <- paste0(intImgPath, match_files[grep('_3', match_files)])
      
      # grep the ROI file
      if (!(nearestPoint$isTest)) {
        match_files <- list.files(path=ROIPath, pattern=t)
        ROI_file <- match_files[grep(paste0('_P', plant_id), match_files)]
      } else{
        match_files <- sample(list.files(path=ROIPath))
        ROI_files <- match_files[grep(paste0('_P', plant_id), match_files)]
        ROI_file <- ROI_files[1]
      }
      nearestPoint$ROIPath <- paste0(ROIPath, ROI_file)
    }
  })
  
  # load the data to get the info about the nearest point
  data <- reactive({
    print('loading data for point clicking...')
    #path <- paste0(plotPath, '/', 'EG_METRIC_1', '/data.table.rds')
    path <- paste0(plotPath, '/', input$images_metric, '/data.table.rds')
    data <- readRDS(path)
  })
  
  # render info about selected plot
  output$clickInfo <- renderTable({
    if (!(is.null(nearestPoint$d))) {
      outTab <- nearestPoint$d[, c('datetime', 'plant.group', 'plant.id')]
      outTab$datetime <- as.character(outTab$datetime)
    } else{
      outTab <- NULL
    }
    print(outTab)
    outTab
  })
  
  # render master plot
  output$imgSelectDataPlot <- renderPlot(
    {
      path <- paste0(plotPath, '/', input$images_metric, '/data.plot.rds')
      p <- readRDS(path)
      return(p)
    }
  )
  
  # render zoomed in plot
  output$imgZoomDataPlot <- renderPlot(
    {
      path <- paste0(plotPath, '/EG_METRIC_1/data.plot.rds')
      path <- paste0(plotPath, '/', input$images_metric, '/data.plot.rds')
      p <- readRDS(path)
      p <- p + coord_cartesian(xlim=ranges$x,
                               ylim=ranges$y,
                               expand=F)
      
      # if have zoomed in, show points
      if (ranges$showPoints) {
        p <- p + geom_point()
        # if have clicked on a point, highlight it
        if (!is.null(nearestPoint$d)) {
          p <- p + geom_point(data=nearestPoint$d, size=5)
        }
      }
      return(p)
    }
  )
  
  #### preprocessing images -------
  # display relevant images for nearestPoint$d datapoint.
  
  output$testWarning <- renderText({
    if (nearestPoint$isTest) {
      'TESTING WARNING: PREPROCESSING IMAGES ARE JUST TEST IMAGES, NOT CORRECT FOR SELECTED POINT!'
    } else {
      NULL
    }
  })
  
  observeEvent(nearestPoint$rawPath, {
    if (!is.null(nearestPoint$rawPath)) {
      output$origImg <- renderImage(
        { 
            path <- nearestPoint$rawPath
            # use w for width and height, as height doesn't change,
            # and are the same anyway
            w <- session$clientData$output_origImg_width
            list(src=path,
                 width=w)
      
        }, deleteFile=F)
      
      output$origImgPath <- renderText(nearestPoint$rawPath)
    }
  })
  
  observeEvent(nearestPoint$maskPath, {
    if (!is.null(nearestPoint$maskPath)) {
        output$maskImg <- renderImage(
          {
            path <- nearestPoint$maskPath
            # use w for width and height, as height doesn't change,
            # and are the same anyway
            w <- session$clientData$output_maskImg_width
            list(src=path,
                 width=w)
          }, deleteFile=F)
        output$maskImgPath <- renderText(nearestPoint$maskPath)
        
    }
  })
  
  observeEvent(nearestPoint$boxPath, {
    if (!is.null(nearestPoint$boxPath)) {
      output$boxImg <- renderImage(
        {
          path <- nearestPoint$boxPath
          # use w for width and height, as height doesn't change,
          # and are the same anyway
          w <- session$clientData$output_boxImg_width
          list(src=path,
               width=w)
        }, deleteFile=F)
      output$boxImgPath <- renderText(nearestPoint$boxPath)
      
    }
  })
  
  observeEvent(nearestPoint$ROIPath, {
    if (!is.null(nearestPoint$ROIPath)) {
      output$ROIImg <- renderImage(
        {
          path <- nearestPoint$ROIPath
          # use w for width and height, as height doesn't change,
          # and are the same anyway
          w <- session$clientData$output_ROIImg_width
          list(src=path,
               width=w)
        }, deleteFile=F)
      output$ROIImgPath <- renderText(nearestPoint$ROIPath)
    }
  })
}

  
  
  
  