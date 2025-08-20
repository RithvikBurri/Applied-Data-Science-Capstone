# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Build dropdown options
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
                 ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    marks={0: '0',
                           2500: '2500',
                           5000: '5000',
                           7500: '7500',
                           10000: '10000'},
                    value=[min_payload, max_payload]
                    ),
    html.Br(),
    
    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])
# TASK 2: Callback for pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Count total successes per site
        success_counts = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(success_counts, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Successful Launches by Site')
    else:
        # Filter by the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count successes vs failures
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        success_fail_counts['class'] = success_fail_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(success_fail_counts, 
                     values='count', 
                     names='class', 
                     title=f'Success vs Failure for site {entered_site}')
    
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Payload vs. Outcome for {entered_site} (Payload Range: {low}-{high} kg)'
    else:
        title = f'Payload vs. Outcome for All Sites (Payload Range: {low}-{high} kg)'
    
    fig = px.scatter(filtered_df, 
                     x='Payload Mass (kg)', 
                     y='class',
                     color='Booster Version Category',
                     title=title,
                     labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
                     hover_data=['Launch Site', 'Booster Version'])
    
    fig.update_yaxes(tickvals=[0, 1], ticktext=['Failure', 'Success'])
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8051)
