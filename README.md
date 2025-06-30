# CrashTrends-ATSIP2025
Stripped down versions of code required for Crash Trends presentation by Michael Allen at ATSIP TRF 2025.

The scripts in this project are capable of making lots of data files and images very quickly. 
Make sure you have a dedicated directory for this data.

# Data Selection
There are 4 scripts used to select data from your crash database.

These scripts assume you have a centralized database with a table dedicated to the details of crashes statewide. 

All data is aggregated by Crash Date. So each row in the output CSVs will be counts of crashes. 

For each script, modify the SQL query to fit your needs and select the data in which you're interested. 

For simplicity, **keep the crash categories the same across data selections**. This makes the later steps easier. 

* _loop_queries.py_
  * Loops over counties and Highway Classes
  * Creates a CSV for each county x Highway Class pair
  * Creates folder for each county (if it doesn't already exist)
* _loop_no_hwy_class.py_
  * Loops over counties
  * Creates a CSV for each county
  * Creates folder for each county (if it doesn't already exist)
* _loop_statewide.py_
  * Loops over Highway Classes across the whole state
  * Creates a CSV for each Highway Class across the state
* _statewide_all.py_
  * Selects data across whole state
  * Creates one CSV for the whole state 

---


# Data Preparation
* _weekConvert.R_
  * Specify which fields are in data grouped by Highway Class and which fields are in data not grouped by Highway Class
  * Loops through all data directories
  * Reads in all CSV files, saves each as tsibble (time series table)
    * Creates Week field from Crash Date
    * Data grouped and aggregated on Week field
    * Week set as index
  * If file is a specific Highway Class, the Highway Class is set as the key. 
  * All tsibbles saved in memory in list called Crashes_w_list


---
# Graph Generation
* _make_sub_dirs.py_
  * Creates a directory for each county (if not already made)
  * Within each county directory, creates directory for each type of graph
  * Within each decomposition directory, creates a directory for each crash count field

* _explore_graphs.R_
  * Loops through all items in Crashes_w_list
  * Skips datasets that have fewer than 50 rows or fewer than an average of 20 crashes per week.
  * For datasets **not grouped** by Highway Class
    * Create moving average values for specified fields
    * Create moving average graph for each specified field
    * Create time series decomposition graph for each specified field
      * Skipping fields with fewer than 5 crashes per week on average
  * For datasets **grouped** by Highway Class
    * Create moving average values for the crash count only
    * Create moving average graph for crash count only
    * Create time series decomposition graph for each specified field
      * Skipping fields with fewer than 5 crashes per week on average

The directories in your project will look something like the below structure. 
```
TrendsProject
├── County1
│   ├── decomp
│   │   ├── crashCount
│   │   │   ├── County1_all.jpg
│   │   │   └── County1_20.jpg
│   │   ├── Pedestrian
│   │   │   ├── County1_all.jpg
│   │   │   └── County1_20.jpg
│   ├── moving_avg
│   │   ├── County1_all.jpg
│   │   └── County1_all NonMotorist.jpg
│   ├── County1_all.csv
│   └── County1_20.csv
└── County2
    ├── decomp
    │   ├── crashCount
    │   │   ├── County2_all.jpg
    │   │   └── County2_20.jpg
    │   ├── Pedestrian
    │   │   ├── County2_all.jpg
    │   │   └── County2_20.jpg
    ├── moving_avg
    │   ├── County2_all.jpg
    │   └── County2_all NonMotorist.jpg
    ├── County2_all.csv
    └── County2_20.csv
```

---
### Organization Scripts
The graph generation process can create lots of graphs very quickly. Due to this, there are some organizational scripts
that will simplify the process of reviewing output. 

The graphing script may create empty directories during the process. This may make it difficult to find useful graphs.
* _rename_empty_dirs.py_
  * Parses through all directories in the project
  * Checks if the directories are empty
  * If a directory is empty, rename with "-EMPTY" suffix. 

If directories have the "-EMPTY" suffix, but you want to run the process again, you'll need to remove the suffix.
* _remove_dir_suffix.py_
  * Parses through all directories in the project
  * Checks if directories have "-EMPTY" suffix
  * Removes suffix and renames directories


# Forecasting
The forecasting portion of this project is much more direct and focused. 
After examining the previously made graphs and consulting with stakeholders for crash types of interest,  

* _crash_forecasting.R_
  * Config
    * Select dataset from Crashes_w_list
    * Select field from selected dataset
    * Select Train/Test Split Proportion
  * Extra Data
    * Import external data for use as predictors
    * Convert external data to weekly, if needed
    * Combine data into single table
  * Variable Transformation
    * Perform transformation on response or predictor variables, as desired.
  * Model Fitting
    * Split data into Train and Test sets
    * Define models and variables (naive, snaive, and drift are baseline models)
    * Fit models (this may take a few minutes)
  * Model Evaluation
    * Prints out various metrics to determine which models performed the best. 
      * RMSE and MAPE are some of the best metrics to look at
  * Graphing
    * Choose a specific model to plot forecast graphs 
    * Save forecast graph to appropriate directory
    * Examine residuals
    