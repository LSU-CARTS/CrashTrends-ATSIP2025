"""
This script creates directories for each county.

Within each county, it creates subdirectories for each crash category of interest.
"""

import os

county_dict = {
    1:  "County_1",
    2:  "County_2",
    3:  "County_3",
    -1: "NOT REPORTED"
}

# These are the crash count fields you want graphs for.
# They each get their own folder per county for organization purposes.
fields = ['crashCount',
'Pedestrian',
'Bicycle',
'Motorcycle',
'RoadwayDeparture',
'Urban',
'Rural'
]

# Each county gets a folder for Moving Averages, Time Series Decomposition, and Normalized Metric Trends
# Each crash category gets a dedicated folder inside decomp
for c in county_dict.values():
    os.mkdir(c)
    os.mkdir(f"{c}/moving_avg")
    os.mkdir(f"{c}/decomp")
    # os.mkdir(f"{c}/norm_metric_trends")
    for f in fields:
        if not os.path.exists(f"{c}/decomp/{f}"):
            os.mkdir(f"{c}/decomp/{f}")
