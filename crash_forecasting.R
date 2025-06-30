# This script assumes you have already run weekConvert and explore_graphs scripts.
# The Crashes_w_list object must be present in memory.


library(tidyverse)
library(fpp3)
library(lubridate)
library(urca)
library(readxl)


#=================== Functions =========================================================
ttsplit=function(p,dataset) {
  # Ensure p is between 0 and 1
  if (p < 0 || p > 1) {
    stop("Proportion 'p' must be between 0 and 1.")
  }
  k <- floor((1 - p) * nrow(dataset))
  Train <- dataset[1:k, ]
  Test <- dataset[(k + 1):nrow(dataset), ]
  return(list(Train = Train, Test = Test))
}
graph_save <- function(graph,graph_name,graph_path) {
  ggsave(paste0(graph_path,graph_name,".jpg"),graph,width=15,height=8)
}

#=================== Config =================== 
# Set which dataset you want to select (Remember to specify a hwy class or all)
data_name <- 'STATEWIDE_all'

# Set which variable in selected dataset you want to forecast 
response_var <- sym('crashCount')

# Set Current Data
cur_data <- Crashes_w_list[[data_name]]

# Set Train/Test Split Proportion
p = 0.2

# Set File Path to Save Graphs
location = strsplit(data_name,"_")[[1]][[1]]
graph_path = sprintf("./%s/Forecasts/",location)


#=================== Extra Data ===================
# If you have data you want to use as predictors that aren't in the crash data already
# bring them in here. 
Covid <- read_excel('./covid data.xlsx')
Snow <- read_excel('./snow storm data.xlsx')
Holidays <- read.csv('./holiday dates.csv')

# If your additional data is aggregated daily, convert to weekly here

# ===== Covid 
Covid_w <- Covid |>
  mutate(Week = yearweek(date)) |>
  group_by(Week) |>
  summarise(covid = max(covid)) |>
  as_tsibble(index=Week) |>
  ungroup()

# ===== Holiday 
Holiday_w <- Holidays |>
  mutate(Week = yearweek(date)) |>
  group_by(Week) |>
  summarise(holiday = max(holiday)) |>
  as_tsibble(index=Week) |>
  ungroup()

# ===== Snow Storms
Snow_w <- Snow |>
  mutate(Week = yearweek(date)) |>
  group_by(Week) |>
  summarise(snow_storms = max(snow_storms)) |>
  as_tsibble(index=Week) |>
  ungroup()

# ==== Add Extra Data to Current Dataset ====
tables_list=list(cur_data,Covid_w,Holiday_w,Snow_w)
cur_data <- tables_list |> 
  reduce(left_join, by = c("Week"))|>
  mutate(across(everything(), ~ replace_na(., 0)))

#  Remove any unwanted fields (i.e. the Moving Average fields)
cur_data <- select(cur_data,-contains("-MA"))

# Create even year breaks for graph output
cur_data <- cur_data |>
  mutate(
    Date = yearweek(Week, week_start = 1) # Convert to yearweek format
  )
year_breaks <- cur_data |>
  filter(str_detect(Week, "W01")) |>
  pull(Date)

#=================== Variable Transformation =================== 
# If you want to transform your response variable, use this space for
# exploring if that's necessary and making the transformation. 



#=================== Main Analysis =============================================
# Split into Train and Test data
splits=ttsplit(p,cur_data)
Train <- splits$Train
Test <- splits$Test

cur_models <- Train |>
  model(naive = NAIVE(!!response_var),
        snaive = SNAIVE(!!response_var),
        drift = RW(!!response_var ~ drift()),
        tslm_base = TSLM(!!response_var ~ trend() + season()),
        tslm_inter = TSLM(!!response_var ~ trend() + season() + trend() * season() + covid + holiday + Rainfall + snow_storms),
        tslm_vars = TSLM(!!response_var ~ trend() + season() + covid + holiday + Rainfall + snow_storms),
        arima_plain = ARIMA(!!response_var, stepwise = TRUE),
        arima_full = ARIMA(!!response_var ~ trend() + season() + covid + holiday + Rainfall + snow_storms, stepwise = TRUE),
        arima_sdif = ARIMA(!!response_var ~ PDQ(0,0,0) + trend() + season() + covid + holiday + Rainfall + snow_storms, stepwise = TRUE),
        #nn_base = NNETAR(response_var, n_networks = 10),
        #nn_vars = NNETAR(response_var~ home + covid + holiday, n_networks = 10)
  )

# ==== Model Evaluation ====
glance(cur_models) |> arrange(AICc) |> select(.model:BIC)
accuracy(cur_models) |> arrange(RMSE)

# ==== Forecasting ====
cur_for <- cur_models |> forecast(Test)
ac_cur <- accuracy(cur_for,Test) |> arrange(RMSE)
ac_cur
accuracy(cur_for,bind_rows(Train,Test)) |> arrange(RMSE)
# ==== Graphing ====
# Pick a model to graph
chosen_model <- "arima_full"

# Graph response variable and forecasted values
for_graph <- cur_for |>
  filter(.model==chosen_model) |>
  autoplot(bind_rows(Train,Test),level = c(80,90,95)) +
  labs(title = paste(chosen_model,data_name,response_var)) +
  scale_x_yearweek(
    name = "Year",
    breaks = year_breaks,   # Use only first weeks of each year
    labels = year(year_breaks))

for_graph
graph_save(for_graph, paste(data_name,response_var,chosen_model), graph_path)

# Plots for Residual Examination
cur_models |> select(chosen_model) |> 
  gg_tsresiduals() + labs(title = paste(chosen_model,data_name, response_var))

