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
                                   dataTableOutput('summary_table')
                                   )),
                          p("[end of results]"))


# define user interface as combo of above ------------
ui <- navbarPage('[Nav bar title]', 
                 summary_panel)