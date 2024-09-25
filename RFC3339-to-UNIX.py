from datetime import datetime
import time

# List of RFC3339 timestamps
rfc3339_timestamps = [
    "2024-08-17T08:20:39Z",
    "2024-08-17T08:52:39Z"
]

# Function to convert RFC3339 to UNIX timestamp
def rfc3339_to_unix(rfc3339_timestamp):
    # Parse the RFC3339 timestamp into a datetime object
    dt = datetime.strptime(rfc3339_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    # Convert datetime to UNIX timestamp
    return int(time.mktime(dt.timetuple()))

# Convert and print each UNIX timestamp on a new line
for ts in rfc3339_timestamps:
    unix_timestamp = rfc3339_to_unix(ts)
    print(unix_timestamp)
