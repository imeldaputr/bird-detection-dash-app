from influxdb_client import InfluxDBClient
import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output

# InfluxDB connection details
bucket = "PyTest"
org = "VerteilteSysteme2024"
token = "DOBus2hDiHCqzgb4pC7ttnK-hfD8eqmbG09P5VaGenwxyXQ6C1BgQbLo-rE6kxXZ3ypJ3ldZ-ir6PbFAahq4Ww=="
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)

# Function to query InfluxDB
def query_data():
    query = '''
    from(bucket: "PyTest")
        |> range(start: 2021-09-30T00:00:00Z, stop: 2021-10-01T00:00:00Z)
        |> filter(fn: (r) => r["_field"] == "confidence")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> keep(columns: ["_time", "confidence", "scientific_name"])
    '''
    # Query InfluxDB
    tables = client.query_api().query_data_frame(org=org, query=query)
    
    # Print out raw data for debugging
    print("Raw query result:")
    print(tables)
    
    # Convert to DataFrame
    df = pd.DataFrame(tables)
    
    # Print DataFrame columns and head for inspection
    print("DataFrame columns:", df.columns)
    print("DataFrame head:\n", df.head())
    
    return df

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Bird Species Detection and Classification Dashboard"),
    dcc.Graph(id='species-count'),
    dcc.Graph(id='confidence-over-time'),
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0)  # Refresh every 10 seconds
])

# Callback to update graph
@app.callback(
    [Output('species-count', 'figure'), Output('confidence-over-time', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    # Query data from InfluxDB
    df = query_data()
    
    # Print out DataFrame for debugging
    print(df.columns)
    print(df.head())

    # Check if DataFrame is empty
    if df.empty:
        return (px.bar(title="No Data Available"), px.line(title="No Data Available"))
    
    # Check if 'scientific_name' exists in the DataFrame
    if 'scientific_name' not in df.columns:
        return (px.bar(title="scientific_name column not found"), px.line(title="scientific_name column not found"))
    
    # 1st Graph: Bird species count
    species_count = df['scientific_name'].value_counts().reset_index()
    species_count.columns = ['scientific_name', 'count']
    species_count_fig = px.bar(species_count, x='scientific_name', y='count', title="Bird Species Count")

    # 2nd Graph: Confidence level of each species over time
    confidence_over_time_fig = px.line(
        df,
        x = '_time',
        y = 'confidence',
        color = 'scientific_name', # shoul be different for each species
        title = "Confidence Level Over Time",
        markers = True
    )

    return species_count_fig, confidence_over_time_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
