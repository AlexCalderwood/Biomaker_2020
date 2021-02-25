# load libraries, data ------------------------------------
here::i_am('dashboard/server.R')
library(here)
library(data.table)
library(stringr)
library(DT) # R interface to JavaScript "DataTables" libarary

# path to stats summary
statsPath <- paste0('www/example_output')
# path to statistics timeseries plot
plotPath <- paste0(statsPath, '/plots/')


red = '#D22D5C'
green = '#2CD16B'

# server ---------------------------------------------------

server <- function(input, output, session) {

  # summary results table --------------------------------------------------
  # format table content
  
  summary_table <- fread(paste0(statsPath, '/summary_table.csv'))
  print(summary_table)
  names(summary_table) <- str_replace(names(summary_table), 
                                      pattern='-', 
                                      replacement=' vs ')
  summary_table[summary_table==TRUE] <- 'different'
  summary_table[summary_table==FALSE] <- 'same'
  
  # control table styling
  output$summary_table <- DT::renderDataTable(
    {
      print('rendering table...')
      datatable(summary_table,
               rownames=F,
               options=list(
                 columnDefs=list(list(className='dt-center', targets='_all')))
               ) %>% 
      DT::formatStyle(2:ncol(summary_table),
                  backgroundColor=DT::styleEqual(c('different', 'same'), c(red, green)))
    })
  
  # timeseries plots -------------------------------------------------------
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
}

  
  
  
  