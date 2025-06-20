"""
This script gets daily precipitation
"""

import requests
import pandas as pd
import time

# --------------------------------------------------------------------------
# 1. NOAA API Configuration
# --------------------------------------------------------------------------
NOAA_TOKEN = ""  # Replace with your token
BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"

HEADERS = {
    "token": NOAA_TOKEN
}

# Each County will have a number associated with it with NOAA.
# There are ways to query NOAA's API for the specific county codes
county_dict = {
22001:'ACADIA',
22003:'ALLEN',
22005:'ASCENSION',
22007:'ASSUMPTION',
22009:'AVOYELLES',
22011:'BEAUREGARD',
22013:'BIENVILLE',
22015:'BOSSIER',
22017:'CADDO',
22019:'CALCASIEU',
22021:'CALDWELL',
22023:'CAMERON',
22025:'CATAHOULA',
22027:'CLAIBORNE',
22029:'CONCORDIA',
22031:'DESOTO',
22033:'EAST BATON ROUGE',
22035:'EAST CARROLL',
22037:'EAST FELICIANA',
22039:'EVANGELINE',
22041:'FRANKLIN',
22043:'GRANT',
22045:'IBERIA',
22047:'IBERVILLE',
22049:'JACKSON',
22051:'JEFFERSON',
22053:'JEFFERSON DAVIS',
22055:'LAFAYETTE',
22057:'LAFOURCHE',
22059:'LASALLE',
22061:'LINCOLN',
22063:'LIVINGSTON',
22065:'MADISON',
22067:'MOREHOUSE',
22069:'NATCHITOCHES',
22071:'ORLEANS',
22073:'OUACHITA',
22075:'PLAQUEMINES',
22077:'POINTE COUPEE',
22079:'RAPIDES',
22081:'RED RIVER',
22083:'RICHLAND',
22085:'SABINE',
22087:'ST. BERNARD',
22089:'ST. CHARLES',
22091:'ST. HELENA',
22093:'ST. JAMES',
22095:'ST. JOHN THE BAPTIST',
22097:'ST. LANDRY',
22099:'ST. MARTIN',
22101:'ST. MARY',
22103:'ST. TAMMANY',
22105:'TANGIPAHOA',
22107:'TENSAS',
22109:'TERREBONNE',
22111:'UNION',
22113:'VERMILION',
22115:'VERNON',
22117:'WASHINGTON',
22119:'WEBSTER',
22121:'WEST BATON ROUGE',
22123:'WEST CARROLL',
22125:'WEST FELICIANA',
22127:'WINN'
}


# --------------------------------------------------------------------------
# 3. Retrieve Daily Precipitation Data
# --------------------------------------------------------------------------
def get_daily_precip_by_location(location_id, start_date, end_date):
    """
    Fetches daily precipitation data (PRCP) from the GHCND dataset
    for a single parish (county) location_id between start_date and end_date.
    Returns a list of data dicts or an empty list if nothing is found.
    """
    dataset_id = "GHCND"
    data_type = "PRCP"
    page_size = 1000
    offset = 1  # NOAA’s offset starts at 1, not 0
    all_data = []

    while True:
        params = {
            "datasetid": dataset_id,
            "locationid": f"FIPS:{location_id}",
            "datatypeid": data_type,
            "startdate": start_date,
            "enddate": end_date,
            "limit": page_size,
            "offset": offset,
            "units": "standard",  # 'standard' = inches, 'metric' = mm
            "sortfield": "date",
            "sortorder": "asc"
        }

        def fetch_data_with_retry(url, headers, params, max_tries=5):
            """Fetch data from the NOAA API with retries and exponential backoff."""
            backoff = 1  # initial backoff in seconds
            # data = None
            tries = 0

            while tries < max_tries:
                try:
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        break
                    else:
                        print(f"Error: HTTP {response.status_code}. Retrying in {backoff}s.")
                        time.sleep(backoff)
                        backoff = backoff * 2
                        tries += 1
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}. Retrying in {backoff}s.")
                    time.sleep(backoff)
                    backoff = backoff * 2
                    tries += 1

            return data


        data = fetch_data_with_retry(f"{BASE_URL}/data", headers=HEADERS, params=params)

        results = data.get("results", [])
        if not results:
            break

        all_data.extend(results)

        # If we got fewer than page_size results, we’re done
        if len(results) < page_size:
            break

        offset += page_size
        # Be nice to the API
        time.sleep(0.5)

    return all_data


# --------------------------------------------------------------------------
# 4. Main Execution
# --------------------------------------------------------------------------
if __name__ == "__main__":
    years = ['2018','2019','2020','2021','2022','2023','2024']  # Years of interest
    for YEAR in years:
        START_DATE = f"{YEAR}-01-01"
        END_DATE = f"{YEAR}-12-31"

        # (A) Get the dictionary of parish IDs

        # (B) Create a DataFrame to store combined results
        columns = ["location_id", "parish_name", "station", "date", "datatype", "value"]
        df_all = pd.DataFrame(columns=columns)

        # (C) Loop over each parish and retrieve data
        for location_id, parish_name in county_dict.items():
            print(f"\n--- Retrieving PRCP data for {parish_name} ({location_id}) ---")
            parish_data = get_daily_precip_by_location(location_id, START_DATE, END_DATE)

            # Convert to a Pandas DataFrame
            df_parish = pd.DataFrame(parish_data)

            if not df_parish.empty:
                # NOAA returns: date, station, attributes, datatype, value
                # We’ll store some of them in a structured way
                df_parish["location_id"] = location_id
                df_parish["parish_name"] = parish_name
                # Reorder / rename columns to match our standard
                df_parish = df_parish.rename(columns={"station": "station",
                                                      "date": "date",
                                                      "datatype": "datatype",
                                                      "value": "value"})
                df_parish = df_parish[["location_id", "parish_name", "station", "date", "datatype", "value"]]
                # Append to the master DataFrame
                df_all = pd.concat([df_all, df_parish], ignore_index=True)

        # (D) Now df_all contains daily precipitation data for all parishes
        #     Save to a CSV (or any other format) for further analysis
        df_all.to_csv(f"louisiana_daily_precip_{YEAR}.csv", index=False)
        print(f"\nAll parish data collected and saved to 'louisiana_daily_precip_{YEAR}.csv'.")
