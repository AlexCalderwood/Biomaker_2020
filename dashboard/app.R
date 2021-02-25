here::i_am('dashboard/app.R')
library(here)
library(shiny)

source(here('dashboard', 'ui.R'))
source(here('dashboard', 'server.R'))

# create shiny app object
app <- shiny::shinyApp(ui=ui, 
                server=server, 
                options=list(launch.browser=TRUE))

# run the app in browser. Can run from cmd line, or from within Rstudio.
runApp(app, launch.browser=TRUE)

