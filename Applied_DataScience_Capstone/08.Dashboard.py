# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a list of unique launch sites from the dataframe
launch_sites = spacex_df['Launch Site'].unique()

# Add 'All Sites' option to the dropdown options
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0, 
        max=10000, 
        step=1000,
        marks={i: str(i) for i in range(0, 11000, 1000)},  # Marks for every 1000Kg
        value=[min_payload, max_payload]  # Default range to be the min and max payload values
    ),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        # Show success vs failure for all sites
        fig = px.pie(filtered_df, names='Launch Site', values='class', title='Total Successful Launches (All Sites)')
    else:
        # Filter dataframe for selected site and show success vs failure
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, names='class', title=f'Success vs. Failed Launches at {entered_site}')
    
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)
def get_scatter_chart(entered_site, selected_payload_range):
    # Filter the dataframe based on the selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]
    
    # If a specific site is selected, filter based on that as well
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Create scatter plot for Payload vs. Success, with color labels for Booster Version Category
    fig = px.scatter(
        filtered_df, x='Payload Mass (kg)', y='class',
        color='Booster Version Category',  # Color by Booster Version Category
        title=f'Payload vs. Launch Success (Site: {entered_site if entered_site != "ALL" else "All Sites"})',
        labels={'class': 'Success (1) / Failure (0)', 'Payload Mass (kg)': 'Payload Mass (kg)'}
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
