"""
This script is for looping over multiple SQL queries and gathering/sorting data.

It loops over all Highway Classes you provide.

It relies on the highway classes having a numerical code associated with them.
But it could be modified to not require that.
"""

import csv
import pyodbc
import os

connection_string = (
    "Driver=<Appropriate SQL Driver>;"
    "Server=<Your Server Name>;"
    "Database=<Your Database Name>;"
    "Trusted_Connection=yes;"
)
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

hwy_classes = [12,13,16,19,20,21,22,24,38,39]


for hwy in hwy_classes:
    query = f"""select 
    CrashDate,
    HighwayClass,
    SUM(Pedestrian),
    SUM(Motorcycle),
    SUM(RoadwayDeparture)
    from FactCrash
    where CrashYear between 2018 and 2024
    and HighwayClass = {hwy}
    group by CrashDate, HighwayClass
    order by CrashDate
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # Automatically named STATEWIDE and placed in a directory named STATEWIDE
    csv_filename = f"STATEWIDE_{hwy}.csv"
    csv_path = os.path.join("STATEWIDE", csv_filename)

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




