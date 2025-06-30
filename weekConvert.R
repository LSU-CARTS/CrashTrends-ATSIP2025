# Required libraries
library(tidyverse)   # For read_csv, dplyr, tidyr, etc.
library(tsibble)     # For as_tsibble
library(lubridate)   # For yearweek()

# Parent directory holding all county folders
root_dir <- "/Path/To/Root/Directory"

# Find subfolders (county directories)
county_dirs <- list.dirs(root_dir, recursive = FALSE)

# Create a list to store each weekly tibble
Crashes_w_list <- list()

# ==== Field Names ====
# Fields for Hwy Class and non-Hwy Class data
fields_hwy_class <- c('crashCount',
                     'Pedestrian',
                     'Bicycle',
                     'RoadwayDeparture')

# Additional fields only for non-hwy class data
fields_no_hwy_class <- append(fields_hwy_class, c('Urban','Rural','Rainfall'))


# ==== Weekly Summary Loop ====
for (c_dir in county_dirs) {
  
  # List all CSV files in the current county directory
  csv_files <- list.files(
    path       = c_dir,
    pattern    = "\\.csv$",
    full.names = TRUE
  )
  
  for (csv_file in csv_files) {
    # Read CSV
    Crashes <- read_csv(csv_file, show_col_types = FALSE)
    
    if (nrow(Crashes) == 0) {
      message("skipping due to empty file", csv_file)
      next
    }
    
    
    # Extract county name & "num" from filename, e.g. "ACADIA_12.csv"
    filename <- basename(csv_file)
    parts    <- strsplit(filename, "_")[[1]]
    county   <- parts[1]                         # "ACADIA"
    numVal   <- gsub("\\.csv$", "", parts[2])    # "12" (remove .csv)
    
    if ("HighwayClass" %in% colnames(Crashes)){
      # Convert to weekly with HighwayClass
      Crashes_w <- Crashes %>%
        rename(`Bad Field Name` = `GoodFieldName`) %>%  # Rename fields if needed
        mutate(CrashDate = as.Date(CrashDate)) %>%
        mutate(Week = yearweek(CrashDate)) %>%
        group_by(Week, HighwayClass) %>%
        summarise(
          across(all_of(fields_hwy_class), ~ sum(.x,na.rm = TRUE)),
          .groups     = "drop"
        ) %>%
        separate(Week, into = c("Year", "Week01"), sep = " ", remove = FALSE) %>%
        filter(Year != 2025) %>%  # Sometimes the weekly data spills over into the next year, remove the year after your data selection
        as_tsibble(index = Week, key = HighwayClass)
    } else {
      # Convert to weekly without HighwayClass
      Crashes_w <- Crashes %>%
        rename(`Bad Field Name` = `GoodFieldName`) %>%
        mutate(CrashDate = as.Date(CrashDate)) %>%
        mutate(Week = yearweek(CrashDate)) %>%
        group_by(Week) %>%
        summarise(
          across(all_of(fields_no_hwy_class), ~ sum(.x,na.rm = TRUE)),
          .groups     = "drop"
        ) %>%
        separate(Week, into = c("Year", "Week01"), sep = " ", remove = FALSE) %>%
        filter(Year != 2025) %>%
        as_tsibble(index = Week)
    }
    
    
    
    # Store in the list using the county + num as the name
    list_name <- paste0(county, "_", numVal)
    Crashes_w_list[[list_name]] <- Crashes_w
  }
}

# Now Crashes_w_list is a list of tsibbles, each named like "ACADIA_12", etc.
# E.g. to access that tsibble directly, do:
# Crashes_w_list[["ACADIA_12"]]
