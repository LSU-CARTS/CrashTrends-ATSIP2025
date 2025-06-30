
library(tidyverse)
library(fpp3)
library(lubridate)
library(urca)


#=================== Functions =========================================================
graph_save <- function(graph,graph_name,graph_path) {
  ggsave(paste0(graph_path,graph_name,".jpg"),graph,width=15,height=8)
}

#=================== Data Exploration Including Graphs =================================
# Use the statewide dataset to create year labels for x-axis of graphs
year_breaks <- Crashes_w_list[['STATEWIDE_all']] |>
  filter(str_detect(Week, "W01")) |>
  pull(Week)

for (name in names(Crashes_w_list)) {
  print(name)
  if (nrow(Crashes_w_list[[name]])<50 | mean(Crashes_w_list[[name]][['crashCount']]) < 20.0) {
    message("skipping ",name," due to small number of records.") 
    next
  }
  # ========== ALL =========
  if (str_detect(name,'all')){   # for datasets not split by highway class (additional Rural/Urban fields)
    # Do moving averages only for certain fields
    for (field in c('crashCount','NonMotorist','Fatal','SuspectedSerious','SuspectedMinor','Urban','Rural','LaneDeparture','RoadwayDeparture','IsIntersection','Animal','Workzone','Rainfall')) {

      # Dynamically create field names for moving averages of the above fields
      four_ma = sym(paste('4-MA',field))
      twelve_ma = sym(paste('12-MA',field))
      twenty_six_ma = sym(paste('26-MA',field))
      
      # Create different moving average fields for each field of interest 
      Crashes_w_list[[name]] <- Crashes_w_list[[name]] |>  
        mutate(
          !!four_ma := slider::slide_dbl(!!sym(field), mean,
                                     .before = 1, .after = 2, .complete = TRUE),
          !!twelve_ma := slider::slide_dbl(!!sym(field), mean,
                                       .before = 6, .after = 5, .complete = TRUE),
          !!twenty_six_ma := slider::slide_dbl(!!sym(field), mean,
                                      .before = 12, .after = 13, .complete = TRUE)
        )
      
      c_split = strsplit(name,"_")[[1]]  # get the county name by itself
      graph_path = sprintf("./%s/moving_avg/",c_split[[1]])  # use county and field name to point to correct directory
      print(c_split)
      
      # Create Moving Average plot
      cc_ma <- Crashes_w_list[[name]] |>
        autoplot(!!sym(field), color='grey') +
        geom_line(aes(y = !!four_ma, color = "4-MA")) +
        geom_line(aes(y = !!twelve_ma, color = "12-MA")) +
        geom_line(aes(y = !!twenty_six_ma, color = "26-MA")) +
        scale_color_manual(values = c("4-MA" = "blue", "12-MA" = "green","26-MA"="purple")) +
        theme(legend.position.inside  = c(0.9, 0.12)) +
        scale_x_yearweek(
          name = "Year",
          breaks = year_breaks,   # Use only first weeks of each year
          labels = year(year_breaks) # Extract only the year for labeling
        ) +
        labs(y = 'Crashes',
             title = sprintf('%s Hwy Class %s Moving Avg %s Crashes',c_split[[1]],c_split[[2]],field),
             color = 'Moving Averages')
      
      graph_save(cc_ma, paste(name,field), graph_path)
    }
    for (field in fields_no_hwy_class) {
      if (mean(Crashes_w_list[[name]][[field]]) < 5.0) {
        message("skipping ", name, " ", field, " due to too few records")
        message("Average of ",str(mean(Crashes_w_list[[name]][[field]])), " records.")
        next
      }
      
      c_split = strsplit(name,"_")[[1]]
      graph_path = sprintf("./%s/decomp/%s/",c_split[[1]],field)
      print(c_split)
      message(name, " ",field)
      
      field_sym = sym(field)  # Allows for dynamically changing string of field name into a call 
      
      # Classical Decomp Additive
      CDA=Crashes_w_list[[name]] |>
        fill_gaps(!!field_sym := 0) |>
        model(
          classical_decomposition(!!field_sym, type = 'additive')
        ) |>
        components() |>
        autoplot() + 
        scale_x_yearweek(
          name = "Year",
          breaks = year_breaks,   # Use only first weeks of each year
          labels = year(year_breaks) # Extract only the year for labeling
        ) +
        labs(title=sprintf("Classical additive decomposition of %s Hwy Class %s %s crashes",c_split[[1]],c_split[[2]], field))+
        theme_bw()
      graph_save(CDA,name,graph_path)
    }
  } 
  else {  # ======= Split by Highway Class =======
    # Only care about crashCount Moving Averages for Hwy Class specific datasets
    Crashes_w_list[[name]] <- Crashes_w_list[[name]] |>
      mutate(
        `4-MA` = slider::slide_dbl(crashCount, mean,
                                   .before = 1, .after = 2, .complete = TRUE),
        `12-MA` = slider::slide_dbl(crashCount, mean,
                                     .before = 6, .after = 5, .complete = TRUE),
        `26-MA` = slider::slide_dbl(crashCount, mean,
                                    .before = 12, .after = 13, .complete = TRUE)
      )
    
    c_split = strsplit(name,"_")[[1]]
    graph_path = sprintf("./%s/moving_avg/",c_split[[1]])
    print(c_split)

    # Create Moving Average
    cc_ma <- Crashes_w_list[[name]] |>
      autoplot(crashCount, color='grey') +
      geom_line(aes(y = `4-MA`, color = "4-MA")) +
      geom_line(aes(y = `12-MA`, color = "12-MA")) +
      geom_line(aes(y = `26-MA`, color = "26-MA")) +
      scale_color_manual(values = c("4-MA" = "blue", "12-MA" = "green","26-MA"="purple")) +
      theme(legend.position.inside  = c(0.9, 0.12)) +
      scale_x_yearweek(
        name = "Year",
        breaks = year_breaks,   # Use only first weeks of each year
        labels = year(year_breaks) # Extract only the year for labeling
      ) +
      labs(y = 'Crashes',
           title = sprintf('%s Hwy Class %s Moving Avg Crashes',c_split[[1]],c_split[[2]]),
           color = 'Moving Averages')
    
    graph_save(cc_ma, name, graph_path)
    
    for (field in fields_hwy_class) {
      if (mean(Crashes_w_list[[name]][[field]]) < 5.0) {
        message("skipping ", name, " ", field, " due to too few records")
        next
      }
      c_split = strsplit(name,"_")[[1]]
      graph_path = sprintf("./%s/decomp/%s/",c_split[[1]],field)
      message(name, " ",field)

      field_sym = sym(field)  # Allows for dynamically changing string of field name into a call 
      
      # Classical Decomp Additive
      CDA=Crashes_w_list[[name]] |>
        fill_gaps(!!field_sym := 0) |>
        model(
          classical_decomposition(!!field_sym, type = 'additive')
        ) |>
        components() |>
        autoplot() + 
        scale_x_yearweek(
          name = "Year",
          breaks = year_breaks,   # Use only first weeks of each year
          labels = year(year_breaks) # Extract only the year for labeling
        ) +
        labs(title=sprintf("Classical additive decomposition of %s Hwy Class %s %s crashes",c_split[[1]],c_split[[2]],field))+
        theme_bw()
      graph_save(CDA,name,graph_path)
    }
  }
}



