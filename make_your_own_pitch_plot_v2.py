#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import streamlit as st
import types

def my_hash_func(obj):
    # Define your custom hashing logic here if needed
    return hash(str(obj))

@st.cache(hash_funcs={types.FunctionType: my_hash_func})
def load_data():
    url = 'https://github.com/michaelrosen3/pitch_plot_generator/blob/main/pitch_plot_data_excel_v3.xlsx?raw=true'
    response = requests.get(url)
    response.raise_for_status()  # Check for HTTP errors
    return pd.read_excel(BytesIO(response.content))

# Example usage in Streamlit app
data = load_data()

# Load data once
statcast_data = load_data()

def plot_pitch_movement(pitcher_name, start_date, end_date):
    pitcher_data = statcast_data[(statcast_data['player_name'] == pitcher_name) & 
                                 (statcast_data['game_date'] >= start_date) & 
                                 (statcast_data['game_date'] <= end_date)]

    # Get unique pitch types for the pitcher
    pitch_types = pitcher_data['pitch_type'].unique()

    # Define a color palette with more distinct colors
    num_colors = len(pitch_types)
    pitch_color_dict = {
        'FF': '#D22D49', 'FT': '#DE6A04', 'SI': '#FE9D00', 'FC': '#933F2C', 
        'CH': '#1DBE3A', 'FS': '#3BACAC', 'SC': '#60DB33', 'FO': '#55CCAB', 
        'ST': '#DDB33A', 'SL': '#EEE716', 'CU': '#00D1ED', 'KC': '#6236CD', 
        'KN': '#3C44CD'
    }
    colors = [pitch_color_dict.get(pt, '#999999') for pt in pitch_types]

    plt.figure(figsize=(9, 9))
    for i, pitch_type in enumerate(pitch_types):
        pitches = pitcher_data[pitcher_data['pitch_type'] == pitch_type]
        plt.scatter(pitches['pfx_x'] * -12, pitches['pfx_z'] * 12, label=pitch_type, color=colors[i], alpha=0.7)

    # Add labels and title
    plt.axis('square')
    plt.xlabel('Horizontal Movement, pitcher perspective (inches)')
    plt.ylabel('Vertical Movement, pitcher perspective (inches)')
    
    # Format the dates to show only YYYY-MM-DD
    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')
    plt.title(f'{pitcher_name} Pitch Plot ({formatted_start_date} to {formatted_end_date})')

    # Set x and y limits
    plt.xlim(-25, 25)
    plt.ylim(-25, 25)

    # Set x and y ticks
    plt.xticks(ticks=range(-25, 26, 5))
    plt.yticks(ticks=range(-25, 26, 5))

    # Add x-y lines
    plt.axhline(0, color='black', linestyle='--', linewidth=0.5)
    plt.axvline(0, color='black', linestyle='--', linewidth=0.5)

    # Add legend
    plt.legend()

    st.pyplot(plt)

def display_summary_statistics(pitcher_data):
    # Calculate the mean of pfx_x, pfx_z, release_pos_z, and release_speed for each pitch_type
    mean_pfx = pitcher_data.groupby('pitch_type')[['pfx_x', 'pfx_z', 'release_pos_z', 'release_speed']].mean()
    
    # Multiply the pfx_x and pfx_z by 12 to convert from feet to inches
    mean_pfx[['pfx_x', 'pfx_z']] *= 12
    
    # Rename and reorder columns
    mean_pfx.columns = ['Horizontal Break (inches)', 'Induced Vertical Break (inches)', 
                        'Release Height (feet)', 'Velocity (mph)']
    mean_pfx = mean_pfx[['Induced Vertical Break (inches)', 'Horizontal Break (inches)', 
                         'Release Height (feet)', 'Velocity (mph)']]

    # Calculate pitch usage percentage
    pitch_count = pitcher_data['pitch_type'].value_counts(normalize=True) * 100
    pitch_count = pitch_count.round(1)  # Round percentages to 1 decimal place

    # Merge usage percentage into the summary table
    mean_pfx['Usage (%)'] = pitch_count

    # Round all values to one decimal place for cleaner display
    mean_pfx = mean_pfx.round(1)

    # Display the statistics
    st.write("#### Pitch Type Stats")
    st.write(mean_pfx)


# Streamlit app layout
st.title('Pitch Plot Generator')

st.text('FF: Four-Seam Fastball\n'
        'SI: Sinker\n'
        'CH: Changeup\n'
        'CU: Curveball\n'
        'SL: Slider\n'
        'FC: Cutter\n'
        'FS: Splitter\n'
        'KC: Knuckle Curve\n'
        'ST: Sweeper')

statcast_data['game_date'] = pd.to_datetime(statcast_data['game_date'])

# Create a list of unique player names for the dropdown menu
player_names = sorted(statcast_data['player_name'].unique())

# Dropdown menu for player name selection
pitcher_name = st.selectbox('Search player name', [''] + player_names)

if not statcast_data.empty:
    min_date = statcast_data['game_date'].min().date()
    max_date = statcast_data['game_date'].max().date()

    start_date, end_date = st.slider(
        'Select a time window',
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY-MM-DD"
    )

if st.button('Generate Pitch Plot'):
    if pitcher_name in statcast_data['player_name'].unique():
        # Convert start_date and end_date to datetime64[ns]
        start_date_dt = pd.to_datetime(start_date)
        end_date_dt = pd.to_datetime(end_date)
        
        pitcher_data = statcast_data[(statcast_data['player_name'] == pitcher_name) & 
                                     (statcast_data['game_date'] >= start_date_dt) & 
                                     (statcast_data['game_date'] <= end_date_dt)]
        
        plot_pitch_movement(pitcher_name, start_date_dt, end_date_dt)
        display_summary_statistics(pitcher_data)
    else:
        st.write('Player not found. Please check the name and try again.')



