# load libraries, data ------------------------------------
here::i_am('dashboard/server.R')
library(here)
library(data.table)
library(DT)

statsPath <- here('plotting_and_stats', 
                  'example_output_model_A')

summary_table <- fread(paste0(statsPath, '/summary_table.csv'))

red = '#D22D5C'
green = '#2CD16B'

# server ---------------------------------------------------

server <- function(input, output) {
  
  summary_table[summary_table==TRUE] <- 'different'
  summary_table[summary_table==FALSE] <- 'same'
  # format table
  
  output$summary_table <- DT::renderDataTable({datatable(summary_table) %>% 
      formatStyle(2:ncol(summary_table),
                  backgroundColor=DT::styleEqual(c('different', 'same'), 
                                                 c(red, green)))
    })
}