"""
This script is for looping over multiple SQL queries and gathering/sorting data.

It loops over all County/Highway Class pairings you provide.

It relies on all counties and highway classes having a numerical value associated with them.
But it could be modified to not required that.
"""



import csv
import pyodbc
import os


county_dict = {
    1:  "County_1",
    2:  "County_2",
    3:  "County_3",
    -1: "NOT REPORTED"
}

connection_string = (
    "Driver=<Appropriate SQL Driver>;"
    "Server=<Your Server Name>;"
    "Database=<Your Database Name>;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# List of highway classes you want analyzed.
# Doesn't have to be integers as long as it fits in your SQL query.
hwy_classes = [12,13,16,19,20,21,22,24,38,39]

# Loops over each county.
for n,c in county_dict.items():

    # Makes a folder for each county
    if not os.path.exists(c):
        os.makedirs(c)

    # Within each county loops over each provided highway class.
    # Summed fields are examples here. Replace with whatever calculation is needed to get aggregate measures
    #   per county, highway class, and day.
    # Filtering on County and Highway Class
    # Grouping by CrashDate
    for hwy in hwy_classes:
        query = f"""select 
        CrashDate,
        HighwayClass,
        SUM(Pedestrian),
        SUM(Motorcycle),
        SUM(RoadwayDeparture)
        from FactCrash
        where CrashYear between 2018 and 2024
        and CountyCode = {n}
        and HighwayClass = {hwy}
        group by CrashDate
        order by CrashDate
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Create a filename based on county and highway class
        csv_filename = f"{c}_{hwy}.csv"
        csv_path = os.path.join(c, csv_filename)

        # Write the data to CSV
        with open(csv_path, mode="w", newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            headers = [desc[0] for desc in cursor.description]
            writer.writerow(headers)

            for row in rows:
                writer.writerow(row)

        print(f"Created {csv_filename}")

cursor.close()
conn.close()




