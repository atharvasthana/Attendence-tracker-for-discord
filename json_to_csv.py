import json
import csv
import os
from datetime import datetime

# Load the attendance.json file
with open("attendance.json", "r") as f:
    data = json.load(f)

# Organize records week-wise
records_by_week = {}

for uid, info in data.items():
    username = info["username"]
    for session in info["sessions"]:
        check_in = datetime.fromisoformat(session["in"])
        check_out = datetime.fromisoformat(session.get("out")) if "out" in session else None

        # Get ISO week info
        year, week, _ = check_in.isocalendar()
        key = f"{year}-W{week:02d}"
        records_by_week.setdefault(key, [])
        records_by_week[key].append([
            uid, username, "Check-In", check_in.isoformat()
        ])
        if check_out:
            records_by_week[key].append([
                uid, username, "Check-Out", check_out.isoformat()
            ])

# Create a CSV file for each week
for week_key, rows in records_by_week.items():
    filename = f"attendance_{week_key}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["User ID", "Username", "Action", "Timestamp"])
        writer.writerows(rows)

print("✅ Weekly CSVs generated.")
