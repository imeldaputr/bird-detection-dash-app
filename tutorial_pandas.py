import argparse
import pandas as pd
from influxdb_client import InfluxDBClient, Point, WritePrecision

def main(host='localhost', port=8086, token='HjcSHsKjI-0vmCFk5iw8L4y8QKJy2BLM08s2Epuht6B2QRvnjHd2ZRWjNU9YDz4-N5IQfrwM50_4NkxCX-Wc8Q==', org='your_org', bucket='demo-bucket'):
    """Instantiate the connection to the InfluxDB 2.0 client."""
    
    # Initialize the InfluxDB 2.x client
    client = InfluxDBClient(url=f"http://localhost:8086", token=token, org=org)
    write_api = client.write_api(write_options=WritePrecision.NS)
    
    print("Create pandas DataFrame")
    df = pd.DataFrame(data=list(range(30)),
                      index=pd.date_range(start='2014-11-16',
                                          periods=30, freq='H'), columns=['0'])
    
    print("Write DataFrame")
    write_api.write(bucket=bucket, org=org, record=df, data_frame_measurement_name='demo', data_frame_tag_columns=['k1', 'k2'])

    print("Read DataFrame")
    query = f'from(bucket: "{bucket}") |> range(start: -1h)'
    result = client.query_api().query(query, org=org)
    
    for table in result:
        for record in table.records:
            print(record)
    
    print("Delete bucket data is not directly supported via Python API")

def parse_args():
    """Parse the args from main."""
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB 2.x')
    parser.add_argument('--host', type=str, required=False,
                        default='localhost',
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
