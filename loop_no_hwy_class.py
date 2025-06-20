"""
This script is for looping over multiple SQL queries and gathering/sorting data.

It loops over all Counties you provide.

It relies on the counties having a numerical code associated with them.
But it could be modified to not require that.
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

# Loops over each county.
for n,c in county_dict.items():

    # Makes a folder for each county
    if not os.path.exists(c):
        os.makedirs(c)

    # Summed fields are examples here. Replace with whatever calculation is needed to get aggregate measures
    #   per county and day.
    # Filtering on County
    # Grouping by CrashDate
    query = f"""select 
    CrashDate,
        SUM(Pedestrian),
        SUM(Motorcycle),
        SUM(RoadwayDeparture),
        SUM(CASE WHEN RuralUrban = 'URBAN' THEN 1 ELSE 0 END) AS [Urban],
        SUM(CASE WHEN RuralUrban = 'RURAL' THEN 1 ELSE 0 END) AS [Rural]
    from FactCrash
    where CrashYear between 2018 and 2024
    and CountyCode = {n}
    group by CrashDate
    order by CrashDate
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # Create a filename based on county and highway class
    csv_filename = f"{c}_all.csv"
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




