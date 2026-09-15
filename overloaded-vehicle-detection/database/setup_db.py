import sys, os
sys.path.append(os.path.abspath(".."))

import mysql.connector
from config import DB_CONFIG

# Connect to MySQL
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Create table without image/video columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS overloaded_vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type VARCHAR(50),
    timestamp DATETIME
)
""")

conn.commit()
conn.close()
print("✅ Database and table ready (overloaded_vehicles).")
