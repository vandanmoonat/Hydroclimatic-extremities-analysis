import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import os

app = dash.Dash(__name__)

directory_path = 'data'


# Get all files in the directory
all_files = os.listdir(directory_path)

# Filter for files with a ".csv" extension
csv_files = [file for file in all_files]

# Create relative paths
relative_paths = [os.path.join(directory_path, file) for file in csv_files]
data_files = relative_paths
# Dropdown options for file selection

# dropdown_options = [{'label': file, 'value': file} for file in data_files]
dropdown_options = [{'label': f'City {i+1}', 'value': file} for i, file in enumerate(data_files)]


def plot_data(path):
    df_station1 = pd.read_csv(path, sep=' ')
    
    # Sorting arrays
    rainfall_array_sorted = df_station1["Rainfall"].sort_values(ascending=False, ignore_index=True)
    tmax_array_sorted = df_station1["Tmax"].sort_values(ascending=False, ignore_index=True)
    wspeed_array_sorted = df_station1["WindSpeed"].sort_values(ascending=False, ignore_index=True)
    tmin_array_sorted = df_station1["Tmin"].sort_values(ignore_index=True)

    # Rainfall percentiles
    rainfall_s1percentile1 = rainfall_array_sorted[263]
    rainfall_s1percentile5 = rainfall_array_sorted[263 * 5]
    rainfall_s1percentile10 = rainfall_array_sorted[263 * 10]

    # Create DataFrames for rainfalls
    df1 = create_df_for_threshold(df_station1, 'Rainfall', rainfall_s1percentile1)
    df2 = create_df_for_threshold(df_station1, 'Rainfall', rainfall_s1percentile5)
    df3 = create_df_for_threshold(df_station1, 'Rainfall', rainfall_s1percentile10)

    # TMax percentiles
    tmax_s1percentile1 = tmax_array_sorted[263]
    tmax_s1percentile5 = tmax_array_sorted[263 * 5]
    tmax_s1percentile10 = tmax_array_sorted[263 * 10]

    # Create DataFrames for TMax
    tmax_df1 = create_df_for_threshold(df_station1, 'Tmax', tmax_s1percentile1)
    tmax_df2 = create_df_for_threshold(df_station1, 'Tmax', tmax_s1percentile5)
    tmax_df3 = create_df_for_threshold(df_station1, 'Tmax', tmax_s1percentile10)

    # WindSpeed percentiles
    wspeed_s1percentile1 = wspeed_array_sorted[263]
    wspeed_s1percentile5 = wspeed_array_sorted[263 * 5]
    wspeed_s1percentile10 = wspeed_array_sorted[263 * 10]

    # Create DataFrames for WindSpeed
    wspeed_df1 = create_df_for_threshold(df_station1, 'WindSpeed', wspeed_s1percentile1)
    wspeed_df2 = create_df_for_threshold(df_station1, 'WindSpeed', wspeed_s1percentile5)
    wspeed_df3 = create_df_for_threshold(df_station1, 'WindSpeed', wspeed_s1percentile10)

    # Tmin percentiles
    tmin_s1percentile1 = tmin_array_sorted[263]
    tmin_s1percentile5 = tmin_array_sorted[263 * 5]
    tmin_s1percentile10 = tmin_array_sorted[263 * 10]

    # Create DataFrames for Tmin
    tmin_df1 = create_df_for_threshold(df_station1, 'Tmin', tmin_s1percentile1, is_less_than=True)
    tmin_df2 = create_df_for_threshold(df_station1, 'Tmin', tmin_s1percentile5, is_less_than=True)
    tmin_df3 = create_df_for_threshold(df_station1, 'Tmin', tmin_s1percentile10, is_less_than=True)

    # Drought analysis
    yearly_rainfall = [np.sum(df_station1.iloc[i * 365 + 150:i * 365 + 271]["Rainfall"]) for i in range(72)]
    np_arr = np.array(yearly_rainfall)
    r_mean = np.mean(np_arr)
    r_std = np.std(np_arr)
    anomaly = ((np_arr - r_mean) * 100) / r_mean
    spi = (np_arr - r_mean) / r_std

    # Create subplots
    fig = make_subplots(rows=4, cols=3, subplot_titles=("Rainfall P1", "Rainfall P5", "Rainfall P10",
                                                        "Tmax P1", "Tmax P5", "Tmax P10",
                                                        "Tmin P1", "Tmin P5", "Tmin P10",
                                                        "WindSpeed P1", "WindSpeed P5", "WindSpeed P10",
                                                        "Anomaly", "SPI"))

    # Plotting
    add_subplot(fig, df1["Count"], 1, 1, "Year", "Count", "Rainfall P1")
    add_subplot(fig, df2["Count"], 1, 2, "Year", "Count", "Rainfall P5")
    add_subplot(fig, df3["Count"], 1, 3, "Year", "Count", "Rainfall P10")
    add_subplot(fig, tmax_df1["Count"], 2, 1, "Year", "Count", "Tmax P1")
    add_subplot(fig, tmax_df2["Count"], 2, 2, "Year", "Count", "Tmax P5")
    add_subplot(fig, tmax_df3["Count"], 2, 3, "Year", "Count", "Tmax P10")
    add_subplot(fig, tmin_df1["Count"], 3, 1, "Year", "Count", "Tmin P1")
    add_subplot(fig, tmin_df2["Count"], 3, 2, "Year", "Count", "Tmin P5")
    add_subplot(fig, tmin_df3["Count"], 3, 3, "Year", "Count", "Tmin P10")
    add_subplot(fig, wspeed_df1["Count"], 4, 1, "Year", "Count", "WindSpeed P1")
    add_subplot(fig, wspeed_df2["Count"], 4, 2, "Year", "Count", "WindSpeed P5")
    add_subplot(fig, wspeed_df3["Count"], 4, 3, "Year", "Count", "WindSpeed P10")
    add_subplot(fig, anomaly, 4, 1, "Year", "Anomaly", "Anomaly")
    add_subplot(fig, spi, 4, 2, "Year", "SPI", "SPI")

    fig.update_layout(showlegend=False)
    return fig

def create_df_for_threshold(df, column, threshold, is_less_than=False):
    data = []
    for i in range(72):
        section = df[i * 365: ((i + 1) * 365 + 1)]
        if is_less_than:
            count = (section[column] < threshold).sum()
        else:
            count = (section[column] > threshold).sum()
        data.append([i, count])
    col = ['Year', 'Count']
    return pd.DataFrame(data, columns=col)

def add_subplot(fig, values, row, col, x_label, y_label, title):
    trace = go.Bar(x=list(range(1951, 2023)), y=values)
    fig.add_trace(trace, row=row, col=col)
    fig.update_xaxes(title_text=x_label, row=row, col=col)
    fig.update_yaxes(title_text=y_label, row=row, col=col)
    fig.update_layout(title_text=title)

# Example usage
# plot_data("data/data_27.125_88.125")
# Define app layout
app.layout = html.Div(style={
    'background': 'linear-gradient(45deg, #203281, #0c64b9, #0098f4)',
    'height': '200vh',  # Set the height to 100% of the viewport height
    'padding': '20px' ,  # Add padding for content visibility
    'margin' : '0',
    'overflow' : 'hidden'
}, children=[
    html.H1("Hydroclimatic extremities analysis", style={'text-align': 'center','color':'#ffe142'}),
    html.H2("B.Tech Project", style={'text-align': 'center','color':'white'}),
    html.H3("Vandan Moonat(B20CI046)", style={'text-align': 'center','color':'white'}),
    # Dropdown for file selection
    dcc.Dropdown(
        id='file-dropdown',
        options=dropdown_options,
        value=data_files[0],  # Set the default selected file
        style={'width': '50%','margin':'auto','box-shadow': '0 0 0 rgba(0, 0, 128, 0.9)'}
    ),
    html.H3("Plots are as follows",style={'text-align':'center','color':'white'}),
    # Display the plot
    dcc.Graph(id='weather-plot', figure=plot_data(data_files[0]),style={'width': '80%', 'height': '900px', 'margin': 'auto', 'background-color': 'rgba(255, 0, 0, 0)','box-shadow': '0 4px 8px rgba(0, 0, 128, 0.9)'}),
    
])

# Define callback to update the plot based on file selection
@app.callback(
    Output('weather-plot', 'figure'),
    [Input('file-dropdown', 'value')]
)
def update_plot(selected_file):
    return plot_data(selected_file)

if __name__ == '__main__':
    app.run_server(debug=True)

