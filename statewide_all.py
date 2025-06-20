"""
This script is for getting crash counts across the whole state without grouping.
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

# Summed fields are examples here.
# Replace with whatever calculation is needed to get aggregate measures
query = f"""select 
CrashDate,
    COUNT(1) AS crashCount,
    SUM(Pedestrian),
    SUM(Motorcycle),
    SUM(RoadwayDeparture)
from FactCrash
where CrashYear between 2018 and 2024
group by CrashDate
order by CrashDate
"""

cursor.execute(query)
rows = cursor.fetchall()

# Only gets one dataset and makes one file
csv_filename = f"STATEWIDE_all.csv"
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




