#!/usr/bin/env python3
"""
Visualization Script for COVID-19 Dashboard
Creates interactive dashboard using Plotly Dash
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

# Load data
def load_data():
    """Load the generated data files"""
    try:
        # Load main dataframe
        df = pd.read_csv('data/dataframe.csv')
        df['date'] = pd.to_datetime(df['date'])
        
        # Load summary stats
        stats_df = pd.read_csv('data/dataframe2.csv')
        
        # Load numpy array (optional, for demonstration)
        np_data = np.load('data/sample.npy')
        
        return df, stats_df, np_data
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run data_gen.py first to generate the data files.")
        return None, None, None

def create_dashboard_figure(df, stats):
    """Create the main dashboard figure with subplots"""
    
    # Create subplots with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Weekly COVID-19 Cases', 'Weekly COVID-19 Deaths', 
                       'Cases vs Deaths Correlation', 'Summary Statistics'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": True}, {"type": "table"}]],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Cases chart (top left)
    fig.add_trace(
        go.Scatter(
            x=df['week_label'],
            y=df['cases'],
            mode='lines+markers',
            name='Weekly Cases',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8, color='#3498db', line=dict(width=2, color='white')),
            hovertemplate='<b>%{x}</b><br>Cases: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Deaths chart (top right)
    fig.add_trace(
        go.Scatter(
            x=df['week_label'],
            y=df['deaths'],
            mode='lines+markers',
            name='Weekly Deaths',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8, color='#e74c3c', line=dict(width=2, color='white')),
            hovertemplate='<b>%{x}</b><br>Deaths: %{y:,.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Correlation chart (bottom left) - Both metrics on same chart
    fig.add_trace(
        go.Scatter(
            x=df['week_label'],
            y=df['cases'],
            mode='lines+markers',
            name='Cases',
            line=dict(color='#3498db', width=2),
            marker=dict(size=6, color='#3498db'),
            yaxis='y3',
            hovertemplate='<b>%{x}</b><br>Cases: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['week_label'],
            y=df['deaths'],
            mode='lines+markers',
            name='Deaths',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=6, color='#e74c3c'),
            yaxis='y4',
            hovertemplate='<b>%{x}</b><br>Deaths: %{y:,.0f}<extra></extra>'
        ),
        row=2, col=1, secondary_y=True
    )
    
    # Summary statistics table (bottom right)
    fig.add_trace(
        go.Table(
            header=dict(
                values=['Metric', 'Value'],
                fill_color='#34495e',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[
                    ['New Cases (28 days)', 'New Deaths (28 days)', 'Case Fatality Rate', 'Reporting Countries'],
                    [f"{stats['total_cases_28d'].iloc[0]:,.0f}", 
                     f"{stats['total_deaths_28d'].iloc[0]:,.0f}", 
                     f"{stats['case_fatality_rate'].iloc[0]:.1f}%", 
                     f"{stats['reporting_countries'].iloc[0]:.0f}"]
                ],
                fill_color='#ecf0f1',
                font=dict(size=11),
                align='left'
            )
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='COVID-19 Dashboard - Cases vs Deaths Analysis',
            x=0.5,
            font=dict(size=20, color='#2c3e50')
        ),
        showlegend=True,
        height=800,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif', size=10, color='#2c3e50')
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridcolor='#ecf0f1', title_font=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor='#ecf0f1', title_font=dict(size=11))
    
    # Set y-axis titles
    fig.update_yaxes(title_text="Number of Cases", row=1, col=1)
    fig.update_yaxes(title_text="Number of Deaths", row=1, col=2)
    fig.update_yaxes(title_text="Cases", row=2, col=1)
    fig.update_yaxes(title_text="Deaths", row=2, col=1, secondary_y=True)
    
    return fig

def create_dash_app(df, stats):
    """Create the Dash application"""
    
    app = dash.Dash(__name__)
    
    # Define the layout
    app.layout = html.Div([
        html.Div([
            html.H1("COVID-19 Dashboard", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
            html.P("Weekly Cases vs Deaths Correlation Analysis", 
                   style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px'})
        ], style={'marginBottom': '30px'}),
        
        # Key metrics cards
        html.Div([
            html.Div([
                html.H3(f"{stats['total_cases_28d'].iloc[0]:,.0f}", 
                       style={'color': '#3498db', 'margin': '0'}),
                html.P("New Cases (28 days)", style={'margin': '5px 0 0 0', 'fontSize': '14px'})
            ], className='stat-card', style={
                'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '10px', 'flex': '1'
            }),
            
            html.Div([
                html.H3(f"{stats['total_deaths_28d'].iloc[0]:,.0f}", 
                       style={'color': '#e74c3c', 'margin': '0'}),
                html.P("New Deaths (28 days)", style={'margin': '5px 0 0 0', 'fontSize': '14px'})
            ], className='stat-card', style={
                'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '10px', 'flex': '1'
            }),
            
            html.Div([
                html.H3(f"{stats['case_fatality_rate'].iloc[0]:.1f}%", 
                       style={'color': '#f39c12', 'margin': '0'}),
                html.P("Case Fatality Rate", style={'margin': '5px 0 0 0', 'fontSize': '14px'})
            ], className='stat-card', style={
                'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '10px', 'flex': '1'
            }),
            
            html.Div([
                html.H3(f"{stats['reporting_countries'].iloc[0]:.0f}", 
                       style={'color': '#9b59b6', 'margin': '0'}),
                html.P("Reporting Countries", style={'margin': '5px 0 0 0', 'fontSize': '14px'})
            ], className='stat-card', style={
                'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '10px',
                'textAlign': 'center', 'margin': '10px', 'flex': '1'
            })
        ], style={'display': 'flex', 'marginBottom': '30px'}),
        
        # Main dashboard figure
        dcc.Graph(
            id='main-dashboard',
            figure=create_dashboard_figure(df, stats),
            style={'height': '800px'}
        ),
        
        # Insights section
        html.Div([
            html.H3("Key Insights", style={'color': '#2c3e50', 'marginBottom': '15px'}),
            html.P([
                "These charts show the correlation between COVID-19 cases and deaths over time. ",
                "Deaths typically follow cases with a 2-3 week lag, and the relationship varies based on ",
                "factors like vaccination rates, treatment improvements, and demographics of affected populations."
            ], style={'lineHeight': '1.6', 'color': '#34495e'})
        ], style={
            'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px',
            'marginTop': '20px', 'borderLeft': '4px solid #3498db'
        })
    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
    
    return app

def save_static_outputs(fig):
    """Save the dashboard as HTML and PNG"""
    
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    # Save as HTML
    fig.write_html("outputs/covid_dashboard.html")
    print("✓ Saved interactive dashboard to outputs/covid_dashboard.html")
    
    # Save as PNG screenshot
    try:
        fig.write_image("outputs/screenshot.png", width=1200, height=800, scale=2)
        print("✓ Saved screenshot to outputs/screenshot.png")
    except Exception as e:
        print(f"⚠ Could not save PNG screenshot: {e}")
        print("  Note: PNG export requires kaleido package: pip install kaleido")

def main():
    """Main function to run the visualization"""
    
    # Load data
    df, stats_df, np_data = load_data()
    if df is None:
        return
    
    print("✓ Data loaded successfully")
    print(f"  - {len(df)} weeks of data")
    print(f"  - Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    
    # Create the main figure
    fig = create_dashboard_figure(df, stats_df)
    
    # Save static outputs
    save_static_outputs(fig)
    
    # Create and run Dash app
    print("\n" + "="*50)
    print("STARTING DASH APPLICATION")
    print("="*50)
    print("Dashboard will be available at: http://127.0.0.1:8050/")
    print("Press Ctrl+C to stop the server")
    
    app = create_dash_app(df, stats_df)
    
    try:
        app.run_server(debug=True, port=8050)
    except KeyboardInterrupt:
        print("\n✓ Dashboard server stopped")

if __name__ == "__main__":
    main()