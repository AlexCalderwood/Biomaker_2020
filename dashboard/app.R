here::i_am('dashboard/app.R')
library(here)
library(shiny)

source(here('dashboard', 'ui.R'))
source(here('dashboard', 'server.R'))

shiny::shinyApp(ui=ui, server=server)