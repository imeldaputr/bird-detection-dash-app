import os
import pandas as pd
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta
import time

# Convert UNIX timestamp to RFC3339 format
def unix_to_rfc3339(unix_ts):
    return datetime.utcfromtimestamp(unix_ts).strftime('%Y-%m-%dT%H:%M:%SZ')

# Process and edit the CSV file
def process_csv(file_path):
    df = pd.read_csv(file_path)
    
    # Ensure start_second is treated as a number (in case it's read as a string)
    df['start_second'] = pd.to_numeric(df['start_second'], errors='coerce')

    # Extract the UNIX timestamp from the audio location (assume it's the last part after the 12-character HEX)
    df['audio_timestamp'] = df['audio_location'].apply(lambda x: int(x[-10:]))
    
    # Add start_second to the extracted UNIX timestamp to create the _time column
    df['_time'] = df.apply(lambda row: unix_to_rfc3339(row['audio_timestamp'] + row['start_second']), axis=1)
    
    # Structure the data for InfluxDB
    influx_data = []
    for _, row in df.iterrows():
        influx_data.append({
            "measurement": "sensor",
            "tags": {
                "scientific_name": row['scientific_name'],
                "common_name": row['common_name'],
                "audio_location": row['audio_location'],
                "start_second": str(row['start_second']),
                "end_second": str(row['end_second'])
            },
            "fields": {
                "confidence": row['confidence'],
            },
            "time": row['_time']
        })
    
    return influx_data

# Upload data to InfluxDB
def upload_to_influx(influx_data):
    bucket = "PyTest"
    org = "VerteilteSysteme2024"
    token = "DOBus2hDiHCqzgb4pC7ttnK-hfD8eqmbG09P5VaGenwxyXQ6C1BgQbLo-rE6kxXZ3ypJ3ldZ-ir6PbFAahq4Ww=="
    url = "http://localhost:8086"

    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api()
    
    # Write data to InfluxDB
    write_api.write(bucket=bucket, org=org, record=influx_data)

# Monitor the folder for new or modified CSV files
def watch_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)
            influx_data = process_csv(file_path)
            upload_to_influx(influx_data)

# Main function to monitor the folder continuously
if __name__ == "__main__":
    folder_to_watch = "/Users/imeldazep/programmierpraktikum/csv"
    
    while True:
        watch_folder(folder_to_watch)
        time.sleep(10)  # Check the folder every 10 seconds
